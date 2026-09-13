# AI Agents as Products: Memory, Guardrails and Beyond

These examples use local Ollama models, Azerbaijani travel data, deterministic
mock weather, and the local Azerbaijani accommodation database.

## Table of contents

- [Scripts](#scripts)
- [Run the examples](#run-the-examples)
- [Example: conversational short-term memory](#example-conversational-short-term-memory)
- [Example: restoring and continuing from a checkpoint](#example-restoring-and-continuing-from-a-checkpoint)
- [Example: persistent Redis checkpoint restoration](#example-persistent-redis-checkpoint-restoration)
- [Example: router-level guardrail](#example-router-level-guardrail)
- [Example: agent-level guardrails](#example-agent-level-guardrails)

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
- `langgraph_router_level_guardrail.py` applies one domain and location check
  in the outer router before an accepted request reaches either specialist.
- `langgraph_agent_level_guardrail.py` routes first and then applies modern
  `before_agent` middleware inside the selected specialist. Each agent owns its
  guardrail boundary.
- `compose.yaml` runs Redis 8 with RedisJSON and RediSearch, append-only-file
  persistence, and a named Docker volume.

All five Python examples use:

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
project dependencies if needed. Then run any example:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_short_term_memory.py
```

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_checkpoint_restore.py
```

Run the two guardrail examples with:

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_router_level_guardrail.py
```

```powershell
python 04-ai-agents\ai_agents_as_products\langgraph_agent_level_guardrail.py
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

## Example: router-level guardrail

This version performs the scope check in the router before choosing the travel
or accommodation specialist. The router and booking agent also use recent
conversation context, so comparative follow-ups retain the latest city, room
type, and other booking constraints.

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|##############################################################################| 15/15 [00:02<00:00,  5.32it/s]
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Thread ID: 1549c85e-5adf-405c-8f56-1a1a81b4d743
Azerbaijan Travel Assistant — router-level guardrail
Type 'exit' or 'quit' to stop.

You: What is the Bitcoin price today?
Assistant: Sorry, I can only help with travel, weather, and accommodation questions about Azerbaijan.

You: Okay, what is the places in Azerbaijan where I can invest?
Assistant: Sorry, I can only help with travel, weather, and accommodation questions about Azerbaijan.

You: Recommend the most expensive hotels in Baku
Assistant: The most expensive hotel in Baku is the **Caspian View Hotel**.

*   **Address:** 1 Neftchilar Avenue, Baku
*   **Rating:** 4.5
*   **Single Room Price:** 180.0 AZN
*   **Double Room Price:** 260.0 AZN

You: What is the cheapest one?
Assistant: The cheapest hotel in Baku is the **Caspian View Hotel**.

*   **Address:** 1 Neftchilar Avenue, Baku
*   **Rating:** 4.5
*   **Single Room Price:** 180.0 AZN
*   **Double Room Price:** 260.0 AZN

(Note: Currently, this is the only hotel listed in our records for Baku.)

You: what about Quba?
Assistant: In Quba, we have the following accommodation:

**Quba Mountain Retreat**
*   **Address:** 8 Heydar Aliyev Avenue, Quba
*   **Rating:** 4.4
*   **Single Room Price:** 120.0 AZN
*   **Double Room Price:** 180.0 AZN

You: I meant most expensive and cheapest ones there
Assistant: In Quba, the only hotel currently listed is the **Quba Mountain Retreat**, which serves as both the most expensive and the cheapest option available:

*   **Hotel:** Quba Mountain Retreat
*   **Address:** 8 Heydar Aliyev Avenue, Quba
*   **Rating:** 4.4
*   **Single Room Price:** 120.0 AZN
*   **Double Room Price:** 180.0 AZN

You: quit
```

This run is fully correct:

- Non-travel financial requests were rejected.
- Hotel requests reached the SQLite booking tools.
- “Cheapest one” retained Baku.
- “What about Quba?” changed only the city while preserving hotel intent.
- “There” correctly resolved to Quba.
- Most expensive and cheapest are identical because the database currently contains only one hotel per city.

The router-level guardrail and context retention are working as intended.

## Example: agent-level guardrails

This version routes first. The selected `create_agent` specialist then runs its
own `before_agent` scope middleware before its model/tool loop. A destination-only correction inherits the earlier booking intent instead of being treated
as a new general travel-information question.

```text
Downloading Azerbaijani destination pages ...
Fetching pages: 100%|##############################################################################| 15/15 [00:02<00:00,  5.45it/s]
Embedding 415 chunks in batches of 32 ...
Embedded 415/415 chunks
Vector store ready.

Thread ID: 48881648-5d12-4106-ada5-b5cec2440585
Azerbaijan Travel Assistant — agent-level guardrails
Type 'exit' or 'quit' to stop.

You: What attractions should I visit in Paris?
Assistant: Sorry, I can only help with travel, weather, and accommodation questions about Azerbaijan.

You: okay, what is about Quba?
Assistant: Quba is a beautiful destination in Azerbaijan, well-known for its cooler summer climate, stunning mountain scenery, and its reputation as the country's primary source of high-quality apples.

Here are some highlights for your visit:

### **Top Attractions & Sights**
*   **Sakina Khanum Mosque:** A notable landmark in the city.
*   **Red Settlement (Qırmızı Qesebe):** Located on the eastern bank of the Qudailchay River, this is an exclusive community known for its distinctive red-roofed houses.
*   **Balbulaq and Tengealtı:** Recommended spots to visit while in the area.

### **Things to Do & Buy**
*   **Apple Tasting:** Quba is famous for producing over 1,000 types of apples. You can find them in local markets and bazars.
*   **Shopping:** The local markets are great places to buy traditional rugs and carpets, as well as a variety of fresh fruits.

### **Travel Tips**
*   **Getting There:** If you are coming from Baku, you can take a cab from the January 20th or Shamahinka stations. By car, it is about a 2–2.5 hour drive via the M1 highway.
*   **Getting Around:** The city of Quba is easy to navigate on foot.
*   **Nearby Destinations:** If you have extra time, you might consider visiting **Qusar** (just north of Quba), the remote mountain village of **Khinalig**, or the coastal destination of **Khachmaz**.

You: Find a double hotel room in London.
Assistant: Sorry, I can only help with travel, weather, and accommodation questions about Azerbaijan.

You: Sorry, I meant in Quba
Assistant: I found one hotel in Quba with a double room available:

*   **Quba Mountain Retreat**: 180.0 AZN per night (5 rooms available)

You: What about the cheapest one?
Assistant: The cheapest (and only) hotel in Quba with a double room available is:

*   **Quba Mountain Retreat**: 180.0 AZN per night (5 rooms available)

You: are there any in Barda?
Assistant: I'm sorry, but I couldn't find any hotels available in Barda.

You: what towns in Azerbaijan have them?
Assistant: The following towns in Azerbaijan have hotels available:

*   Baku
*   Sheki
*   Ganja
*   Quba
*   Gabala
*   Lankaran
*   Shamakhi
*   Nakhchivan
*   Naftalan
*   Goygol

You: okay, cheapest and most expensive ones in Ganja
Assistant: In Ganja, there is only one hotel with a double room available:

*   **Ganja Garden Hotel**: 155.0 AZN (6 rooms available)

Since it is the only option, it is both the cheapest and the most expensive.

You: what are the interesting places to see there?
Assistant: Ganja is one of the oldest and most historically significant cities in the Caucasus. It is known for its rich architecture and its heritage as the home of Azerbaijan’s national bard, Nizami Gəncəvi.

Here are some interesting things to see and do in Ganja:

### **Historical & Cultural Highlights**
*   **Architecture:** The city is architecturally very interesting due to its long history and the various cultures that have influenced it over the centuries.
*   **Nizami Gəncəvi Heritage:** As the home of the famous national bard, the city holds deep cultural significance for Azerbaijani literature.
*   **Art Collections:** If you are looking for art, the **Chinar Hotel & SPA** features its own private art collection that you can view.

### **Shopping & Markets**
*   **Carpet Trade:** Ganja is well-known as a major center for the carpet trade.
*   **Mərkəzi Bazar (Central Bazaar):** A great place to experience the local atmosphere.
*   **Bazarstore:** A good choice for high-quality food, wines, and cheeses.
*   **Aura Park:** A modern shopping center for more contemporary retail.

### **Travel Tips**
*   **Getting Around:** The town is relatively small and can be easily explored on foot.
*   **Day Trips:** Ganja serves as a gateway to the **Lesser Caucasus** region, making it an excellent base for day trips into the mountains.
*   **Getting There:** You can fly into Ganja International Airport (KVD), which is about 8 km from the city center.

You: can you book place me there?
Assistant: I cannot book accommodations for you directly. I can provide you with availability and pricing information for hotels and BnBs in Azerbaijan, but you will need to complete the booking through the property's own website or a booking platform.

If you would like, I can double-check the current availability and prices for the **Ganja Garden Hotel** or any other property in Ganja for you!

You: quit
```

This run is correct and demonstrates the agent-level architecture well:
- Out-of-scope Paris and London requests were rejected.
- Destination corrections retained booking intent.
- Barda correctly returned no database hotel.
- Hotel-city listing and Ganja pricing used SQLite.
- “Interesting places there” correctly switched to the travel agent while retaining Ganja.
- “Book a place there” returned a limitation because no actual reservation tool/API exists.

For real booking, we would need a booking tool plus confirmation or human-in-the-loop approval.
