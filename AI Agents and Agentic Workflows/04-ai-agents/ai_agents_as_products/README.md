# AI Agents as Products: Memory Examples

These examples use local Ollama models, Azerbaijani travel data, deterministic
mock weather, and the local Azerbaijani accommodation database.

## Scripts

- `langgraph_short_term_memory.py` builds an interactive travel assistant with
  LangGraph `InMemorySaver`. A generated `thread_id` keeps the conversation
  state available across turns while the Python process is running.
- `langgraph_checkpoint_restore.py` reuses the same assistant, lists the saved
  checkpoints for a thread, restores the latest checkpoint explicitly, and
  continues with a context-dependent follow-up question.
- `langgraph_redis_checkpoint_restore.py` saves a thread to Redis and restores
  it in a separate Python process. This demonstrates persistence beyond the
  lifetime of one application process.
- `compose.yaml` runs Redis 8 with RedisJSON and RediSearch, append-only-file
  persistence, and a named Docker volume.

All three scripts use:

- `gemma4:12b-it-q8_0` for chat and tool calling;
- `bge-m3:latest` for embeddings;
- `../multi_agent_systems/hotel_db/azerbaijan_hotels.db` for hotel data;
- Azerbaijani destination pages for retrieval-augmented travel information.

Weather values are deterministic mock data, not live observations.

## Run the examples

Start Ollama and confirm that the local models are available:

```powershell
ollama list
```

From the repository root, activate the virtual environment and install the
project dependencies if needed. Then run either example:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_short_term_memory.py
```

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_checkpoint_restore.py
```

The Redis example also needs the root dependencies and its Docker service:

```powershell
pip install -r requirements.txt
docker compose -f 04-ai-agents\ai_agents_as_products\compose.yaml up -d redis
```

Start a thread and copy the printed thread ID:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_redis_checkpoint_restore.py save --question "Tell me briefly about Quba."
```

Restore it in a new Python process:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_redis_checkpoint_restore.py restore THREAD_ID
```

The `save` and `restore` commands accept `--question`. Without it, `save`
prompts for a question, while `restore` asks the context-dependent default:
`What is the mock weather in the same town?`

Check or stop Redis with:

```powershell
docker compose -f 04-ai-agents\ai_agents_as_products\compose.yaml ps
docker compose -f 04-ai-agents\ai_agents_as_products\compose.yaml down
```

`docker compose down` removes the container and network but retains the named
volume. Set `REDIS_URL` if Redis is not at `redis://localhost:6379`.

Additionally:

```powershell
docker compose -f 04-ai-agents\ai_agents_as_products\compose.yaml down --volumes --remove-orphans
```

This removes the container, Compose network, named Redis volume, and orphaned services. The saved Redis checkpoints will be permanently deleted.

To also remove the downloaded `redis:8` image:

```powershell
docker compose -f 04-ai-agents\ai_agents_as_products\compose.yaml down --volumes --remove-orphans --rmi all
```

**If you are already inside the `ai_agents_as_products` directory**, use:

```powershell
docker compose -f compose.yaml down --volumes --remove-orphans
```

Or simply:

```powershell
docker compose down --volumes --remove-orphans
```

*to not to duplicate the relative directory path.*

```shell
[+] down 3/3
 ✔ Container langgraph-redis                         Removed                                                                    0.4s
 ✔ Volume ai_agents_as_products_langgraph_redis_data Removed                                                                    0.0s
 ✔ Network ai_agents_as_products_default             Removed                                                                    0.3s
``` 

The scripts download and embed the destination pages at startup, so the first
prompt appears only after the vector store is ready.

## Example: conversational short-term memory

The second question refers to Salyan only as `there`. Because both turns use
the same thread, the assistant can resolve that reference from its saved state.

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|...| 15/15
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Thread ID: 750ae5da-692a-4054-b604-6321c2961b18
Azerbaijan Travel Assistant with short-term memory
Type 'exit' or 'quit' to stop.

You: Tell me about Salyan
Assistant: Salyan is a city and the capital of the Salyan District in Azerbaijan. Here are some key facts about the city:
- Economy: The city is industrialized and is particularly well-known for its caviar processing.
- History: During the Mongol invasion of Azerbaijan, the city was referred to as "Dalan-Navur" in Mongolian.
- Geography: It is located in the southern part of Azerbaijan.
- Climate: The region experiences a variety of temperatures throughout the year, with warm summers and cooler winters.
If you are planning a visit and would like to know the current weather conditions, please let me know!

You: yes, tell me the current weather conditions there
Assistant: The current weather in Salyan is sunny with a temperature of 22°C.
(Please note: This is mock weather data and not a live forecast.)

You: quit
```

## Example: restoring and continuing from a checkpoint

One graph invocation creates several checkpoints because LangGraph saves state
at graph super-steps, not only once per user message. The script restores the
newest snapshot and asks about `the same town`; the restored messages let the
assistant infer Tovuz.

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|#############################################################################| 15/15 [00:02<00:00,  5.25it/s]
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Thread ID: 815f044d-68d3-4b28-9df5-3f6fee2a939a
Ask first about an Azerbaijani destination or accommodation.
You: Tell me briefly about Tovuz.
Assistant: Tovuz is a district in Azerbaijan. It is known for its rural landscape and various villages. 

Key highlights include:
*   **Geography:** It is part of the mainland administrative divisions of Azerbaijan.
*   **Local Culture:** The region is associated with traditional regional specialties such as **Tendir Oven** and **Talish Women Gutab**.
*   **Shopping:** Visitors can find traditional **rugs and carpets** in the area.

(Note: While the search results also mentioned Quba's famous apples and specific landmarks like Balbulaq and Tengealtı, those are distinct from the Tovuz district.)

Saved checkpoints: 4
  1. checkpoint_id=1f1af0e7-1ca9-6c30-8002-0e65502dd4d8; next=()
  2. checkpoint_id=1f1af0e6-e0d6-6ae4-8001-b8d7f72879ff; next=('travel_info_agent',)
  3. checkpoint_id=1f1af0e6-c234-614f-8000-e75aa77a523c; next=('router_agent',)
  4. checkpoint_id=1f1af0e6-c232-66de-bfff-c3855c4de087; next=('__start__',)

Restored checkpoint: 1f1af0e7-1ca9-6c30-8002-0e65502dd4d8
Messages in restored state: 4
Next nodes from restored state: ()

You: What is the mock weather in the same town?
Assistant: The mock weather for Tovuz is sunny with a temperature of 28°C.

Checkpoints after continuing: 8
The follow-up could resolve 'the same town' because it continued from the restored thread state.
```

As seen, the checkpoint restoration works correctly:

- First turn created **4 checkpoints**.
- The latest completed checkpoint was restored with **4 messages**.
- The follow-up understood “the same town” as **Tovuz**.
- Continuing from the restored state increased the history to **8 checkpoints**.

*One separate issue*: the Tovuz answer contains unrelated regional details such as “Talish Women Gutab” and Quba references. That *indicates imperfect vector retrieval*, not a memory/checkpoint problem.

## Example: persistent Redis checkpoint restoration

The following was verified with two separate Python processes. The second
process recovered four messages and understood `the same town` as Quba,
confirming that Redis retained the thread after the first process exited.

First process:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_redis_checkpoint_restore.py save --question "Tell me briefly about Quba."
```

```text
Thread ID: 63b0473e-fd10-4f28-940e-b7528e191992
You: Tell me briefly about Quba.
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|...| 15/15
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Assistant: Quba is an ancient city and the major hub of the Quba District in
Azerbaijan. It is known for several features:

- Agriculture: Quba is famous for high-quality apples, with more than 1,000
  varieties.
- Tourism: Its cooler climate and mountain scenery make it a popular summer
  destination.
- Geography and landmarks: The city stands on the western bank of the
  Qudyalchay River; the Red Settlement is on the eastern bank.
- Attractions: These include the Sakina Khanum Mosque and the nearby Balbulaq
  and Tengealti areas.
- Shopping: Visitors often buy traditional carpets and fresh local fruit.
Saved latest Redis checkpoint: 1f1af122-388e-6ef9-8002-797aaded1d08
Run the restore command in a new process with this thread ID to continue the
conversation.
```

Second process:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_redis_checkpoint_restore.py restore 63b0473e-fd10-4f28-940e-b7528e191992
```

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|...| 15/15
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Restored thread: 63b0473e-fd10-4f28-940e-b7528e191992
Latest checkpoint: 1f1af122-388e-6ef9-8002-797aaded1d08
Messages before continuing: 4
You: What is the mock weather in the same town?
Assistant: The mock weather for Quba is currently foggy with a temperature of 23°C.
New latest Redis checkpoint: 1f1af123-438d-6791-8006-5181658576e8
```

`InMemorySaver` loses its checkpoints when the process stops. Use a persistent
checkpointer such as Redis, SQLite, or PostgreSQL when threads must survive
application restarts or be shared by multiple application replicas.
