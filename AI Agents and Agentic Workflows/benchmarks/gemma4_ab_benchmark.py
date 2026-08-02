"""Reproducible Azerbaijani and agentic A/B benchmark for local Gemma 4 models."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


MODELS = ["gemma4:12b-it-q8_0", "gemma4:e4b-it-bf16"]
RESULT_PATH = Path(__file__).parent / "results" / "gemma4_ab_benchmark.json"

MODEL_OPTIONS = {
    "num_ctx": 65_536,
    "temperature": 0.0,
    "seed": 42,
    "top_k": 64,
    "top_p": 0.95,
    "num_predict": 500,
    "reasoning": False,
    "keep_alive": "15m",
}

LANGUAGE_SYSTEM = (
    "Sən Azərbaycan dilində yüksək səviyyədə yazan köməkçisən. "
    "Tapşırığı dəqiq yerinə yetir, yalnız tələb olunan nəticəni ver və "
    "Azərbaycan dilinin orfoqrafiya, qrammatika və üslub normalarına əməl et."
)

LANGUAGE_CASES = [
    {
        "id": "orthography_grammar",
        "category": "orthography and grammar",
        "prompt": (
            "Aşağıdakı mətni orfoqrafik və qrammatik baxımdan düzəlt. İzah vermə, "
            "yalnız düzəldilmiş variantı yaz:\n\n"
            "Mən sabah Bakıya gələcəm və səninlə görüşməy istəyirəm. "
            "Əlbətdəki vaxtın olsa mənə xəbər elə."
        ),
    },
    {
        "id": "formal_writing",
        "category": "formal writing",
        "prompt": (
            "Aşağıdakı qeyri-rəsmi mesajı 70-90 sözlük rəsmi iş e-poçtuna çevir. "
            "Mövzu sətri, müraciət, əsas hissə və nəzakətli sonluq olsun:\n\n"
            "Salam müəllim, layihəni bu gün çatdıra bilmirəm, çünki məlumatlarda "
            "problem çıxdı. İki gün də vaxt versəniz yaxşı olar."
        ),
    },
    {
        "id": "translation_nuance",
        "category": "translation",
        "prompt": (
            "Bu mətni təbii və peşəkar Azərbaycan dilinə tərcümə et:\n\n"
            "Human oversight should not eliminate autonomy; it should make the "
            "agent accountable for high-impact decisions while preserving its "
            "ability to investigate and propose solutions independently."
        ),
    },
    {
        "id": "constraint_following",
        "category": "instruction following",
        "prompt": (
            "Agent əsaslı sistemlərdə təhlükəsizlik haqqında məhz 3 maddə yaz. "
            "Hər maddə 8-12 sözdən ibarət olsun, fel ilə başlasın və heç bir "
            "ingilis sözü işlətmə."
        ),
    },
    {
        "id": "reasoning_consistency",
        "category": "consistency",
        "prompt": (
            "Bir maliyyə köməkçisi istifadəçinin hesab qalığını oxuya, ödəniş "
            "hazırlaya və ödənişi təsdiqləyə bilir. Aşağıdakı üç suala qısa və "
            "ardıcıl cavab ver: 1) Hansı əməl sərbəst icra oluna bilər? 2) Hansı "
            "əməl üçün istifadəçi təsdiqi lazımdır? 3) Niyə?"
        ),
    },
]


class WeatherInput(BaseModel):
    city: str = Field(description="Şəhərin Azərbaycan dilində adı")
    date: Literal["today", "tomorrow"] = Field(description="Bu gün və ya sabah")


class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="Axtarış sorğusu")
    top_k: int = Field(default=3, ge=1, le=5, description="Qaytarılacaq nəticə sayı")


class CustomerInput(BaseModel):
    email: str = Field(description="Müştərinin e-poçt ünvanı")


class OrdersInput(BaseModel):
    customer_id: int = Field(description="Müştərinin tam ədəd identifikatoru")
    limit: int = Field(default=5, ge=1, le=10, description="Son sifarişlərin sayı")


class TicketInput(BaseModel):
    customer_id: int = Field(description="Müştərinin tam ədəd identifikatoru")
    severity: Literal["low", "medium", "high"] = Field(description="Problemin vaciblik səviyyəsi")
    summary: str = Field(description="Problemin Azərbaycan dilində qısa xülasəsi")


TOOL_TRACE: list[dict] = []


@tool(args_schema=WeatherInput)
def get_weather(city: str, date: str) -> dict:
    """Göstərilən şəhər və tarix üçün hava proqnozunu qaytarır."""
    result = {"city": city, "date": date, "temperature_c": 28, "condition": "günəşli"}
    TOOL_TRACE.append({"tool": "get_weather", "args": {"city": city, "date": date}, "result": result})
    return result


@tool(args_schema=KnowledgeSearchInput)
def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    """LangChain və LangGraph texniki bilik bazasında axtarış aparır."""
    result = {
        "query": query,
        "results": [
            "Şərti keçid qraf vəziyyətinə əsasən növbəti düyünü seçir.",
            "Marşrutlaşdırma funksiyası keçidin açarını qaytarır.",
        ][:top_k],
    }
    TOOL_TRACE.append(
        {"tool": "search_knowledge_base", "args": {"query": query, "top_k": top_k}, "result": result}
    )
    return result


@tool(args_schema=CustomerInput)
def lookup_customer(email: str) -> dict:
    """E-poçt ünvanına görə müştərini tapır və identifikatorunu qaytarır."""
    result = {"customer_id": 42, "name": "Leyla Əliyeva", "email": email}
    TOOL_TRACE.append({"tool": "lookup_customer", "args": {"email": email}, "result": result})
    return result


@tool(args_schema=OrdersInput)
def get_orders(customer_id: int, limit: int = 5) -> dict:
    """Müştərinin son sifarişlərini qaytarır."""
    orders = [
        {"order_id": "AZ-1042", "status": "delayed", "amount_azn": 84.50},
        {"order_id": "AZ-1031", "status": "delivered", "amount_azn": 39.90},
    ][:limit]
    result = {"customer_id": customer_id, "orders": orders}
    TOOL_TRACE.append(
        {"tool": "get_orders", "args": {"customer_id": customer_id, "limit": limit}, "result": result}
    )
    return result


@tool(args_schema=TicketInput)
def create_support_ticket(customer_id: int, severity: str, summary: str) -> dict:
    """Gecikmiş sifariş üçün sınaq dəstək bileti yaradır. Bu alət yalnız lokal maketdir."""
    result = {"ticket_id": "TKT-9001", "customer_id": customer_id, "severity": severity, "summary": summary}
    TOOL_TRACE.append(
        {
            "tool": "create_support_ticket",
            "args": {"customer_id": customer_id, "severity": severity, "summary": summary},
            "result": result,
        }
    )
    return result


TOOLS = [get_weather, search_knowledge_base, lookup_customer, get_orders, create_support_ticket]
TOOL_MAP = {item.name: item for item in TOOLS}

TOOL_SYSTEM = (
    "Sən Azərbaycan dilində işləyən agent köməkçisən. İstək uyğun olduqda yalnız təqdim edilmiş "
    "alətlərdən istifadə et. Alət arqumentlərini sxemə tam uyğun yarat, alət nəticələrini uydurma "
    "və bütün lazım olan addımlar bitdikdən sonra Azərbaycan dilində qısa yekun cavab ver."
)

TOOL_SELECTION_CASES = [
    {
        "id": "no_tool",
        "prompt": "Agent əsaslı iş axınının nə olduğunu bir cümlə ilə izah et.",
        "expected_tool": None,
    },
    {
        "id": "weather_tool",
        "prompt": "Sabah Bakı şəhərində hava necə olacaq?",
        "expected_tool": "get_weather",
    },
    {
        "id": "knowledge_tool",
        "prompt": "LangGraph-da şərti keçidin necə işlədiyini bilik bazasında axtar və 2 nəticə gətir.",
        "expected_tool": "search_knowledge_base",
    },
]

MULTI_STEP_PROMPT = (
    "leyla@example.com ünvanlı müştərinin son 2 sifarişini tap. Sifarişlərdən hər hansı biri "
    "gecikibsə, həmin müştəri üçün yüksək vaciblikli dəstək bileti yarat və nəticəni Azərbaycan "
    "dilində qısa şəkildə yekunlaşdır."
)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def make_model(model_name: str) -> ChatOllama:
    return ChatOllama(model=model_name, **MODEL_OPTIONS)


def metadata_from(message: AIMessage, elapsed_seconds: float) -> dict:
    metadata = dict(message.response_metadata or {})
    return {
        "elapsed_seconds": round(elapsed_seconds, 3),
        "prompt_eval_count": metadata.get("prompt_eval_count"),
        "prompt_eval_duration_ns": metadata.get("prompt_eval_duration"),
        "eval_count": metadata.get("eval_count"),
        "eval_duration_ns": metadata.get("eval_duration"),
        "load_duration_ns": metadata.get("load_duration"),
        "total_duration_ns": metadata.get("total_duration"),
    }


def run_language_cases(model: ChatOllama) -> list[dict]:
    results = []
    for case in LANGUAGE_CASES:
        started = time.perf_counter()
        response = model.invoke([SystemMessage(content=LANGUAGE_SYSTEM), HumanMessage(content=case["prompt"])])
        elapsed = time.perf_counter() - started
        results.append(
            {
                **case,
                "response": response.content,
                "reasoning": response.additional_kwargs.get("reasoning_content"),
                "metrics": metadata_from(response, elapsed),
            }
        )
        print(f"  language: {case['id']} complete ({elapsed:.1f}s)", flush=True)
    return results


def run_tool_selection_cases(model: ChatOllama) -> list[dict]:
    bound_model = model.bind_tools(TOOLS)
    results = []
    for case in TOOL_SELECTION_CASES:
        started = time.perf_counter()
        response = bound_model.invoke([SystemMessage(content=TOOL_SYSTEM), HumanMessage(content=case["prompt"])])
        elapsed = time.perf_counter() - started
        results.append(
            {
                **case,
                "response": response.content,
                "tool_calls": response.tool_calls,
                "invalid_tool_calls": response.invalid_tool_calls,
                "metrics": metadata_from(response, elapsed),
            }
        )
        print(f"  tool selection: {case['id']} complete ({elapsed:.1f}s)", flush=True)
    return results


def build_agent_graph(model: ChatOllama):
    bound_model = model.bind_tools(TOOLS)

    def call_model(state: AgentState) -> dict:
        return {"messages": [bound_model.invoke(state["messages"])]}

    def call_tools(state: AgentState) -> dict:
        last_message = state["messages"][-1]
        outputs: list[ToolMessage] = []
        for call in last_message.tool_calls:
            tool_name = call["name"]
            try:
                selected_tool = TOOL_MAP[tool_name]
                result = selected_tool.invoke(call["args"])
                content = json.dumps(result, ensure_ascii=False)
            except Exception as exc:  # Capture schema or selection failures as agent-visible evidence.
                content = json.dumps({"error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False)
            outputs.append(ToolMessage(content=content, tool_call_id=call["id"], name=tool_name))
        return {"messages": outputs}

    def route(state: AgentState) -> str:
        last_message = state["messages"][-1]
        return "tools" if isinstance(last_message, AIMessage) and last_message.tool_calls else END

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", call_tools)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


def serialize_message(message: BaseMessage) -> dict:
    data = {"type": message.type, "content": message.content}
    if isinstance(message, AIMessage):
        data["tool_calls"] = message.tool_calls
        data["invalid_tool_calls"] = message.invalid_tool_calls
    if isinstance(message, ToolMessage):
        data["name"] = message.name
        data["tool_call_id"] = message.tool_call_id
    return data


def run_multi_step_case(model: ChatOllama) -> dict:
    TOOL_TRACE.clear()
    graph = build_agent_graph(model)
    started = time.perf_counter()
    result = graph.invoke(
        {"messages": [SystemMessage(content=TOOL_SYSTEM), HumanMessage(content=MULTI_STEP_PROMPT)]},
        config={"recursion_limit": 12},
    )
    elapsed = time.perf_counter() - started
    return {
        "prompt": MULTI_STEP_PROMPT,
        "expected_tool_sequence": ["lookup_customer", "get_orders", "create_support_ticket"],
        "actual_tool_trace": list(TOOL_TRACE),
        "messages": [serialize_message(message) for message in result["messages"]],
        "elapsed_seconds": round(elapsed, 3),
    }


def command_output(command: list[str]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return (completed.stdout + completed.stderr).strip()


def save_results(results: dict) -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    results = {
        "settings": MODEL_OPTIONS,
        "language_system": LANGUAGE_SYSTEM,
        "tool_system": TOOL_SYSTEM,
        "models": {},
    }
    save_results(results)

    for model_name in MODELS:
        print(f"Benchmarking {model_name}", flush=True)
        model = make_model(model_name)
        model_result = {}
        results["models"][model_name] = model_result
        model_result["language_cases"] = run_language_cases(model)
        save_results(results)
        model_result["tool_selection_cases"] = run_tool_selection_cases(model)
        save_results(results)
        print("  multi-step agent case starting", flush=True)
        model_result["multi_step_agent"] = run_multi_step_case(model)
        model_result["ollama_ps"] = command_output(["ollama", "ps"])
        model_result["nvidia_smi"] = command_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free",
                "--format=csv,noheader",
            ]
        )
        save_results(results)
        print(f"  saved {model_name} evidence", flush=True)
        command_output(["ollama", "stop", model_name])

    print(f"Benchmark complete: {RESULT_PATH}", flush=True)


if __name__ == "__main__":
    main()
