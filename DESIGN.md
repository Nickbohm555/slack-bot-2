# Design

I initially spent time and effort building [slack-bot](https://github.com/Nickbohm555/slack-bot) with the design here if you want to read my initial thoughts: [DESIGN.md](https://github.com/Nickbohm555/slack-bot/blob/main/DESIGN.md). You can read this to get my initial design for how I built this slack-bot (I include notes on dealing with conversation history, auth, initial agent design), then in here I include my improvements that got me from 50-70% accuracy to 85-95% accuracy while reducing latency down to ~30-60 seconds and only 5-8 tool calls on average. If you want to see how I dealt with checkpointer or anything not discussed here, it is probably discussed in the other repo design I linked above.

## TLDR

I had spent a lot of time building out the architecture for a single agent with 3 SQL tools, `sql_list_tables`, `sql_get_schema`, and `sql_execute`. I tried to optimize for planning, speed, and accuracy by using autoresearch to improve my prompt, trying to account for all the different types of questions that could be asked, using a `gpt-4-mini` model to boost speed (so I thought), and messing around with what skills I should call.

I was able to improve my answers from 0% accuracy to around 50% accuracy for each question, but could never pass 60-70% consistently. The reason for this was partially because I was going about context engineering all wrong. I was simply scaling vertically by increasing my prompt to account for more and more scenarios, leaving my entire harness extremely brittle. One would pass but another would fail after every tweak. I knew there was a cap for how well a system like this could perform, even with what I thought were clever tweaks such as making sure we do all tool calls sequentially, using the built-in to-do list effectively, trying skills, etc. I also moved from using gpt-4-mini to gpt-5 model which I think also greatly improved performance being a reasoning model and just better overall. 

## Filesystem Approach

That is when I decided to try an approach similar to https://vercel.com/blog/we-removed-80-percent-of-our-agents-tools. I built a single source of truth filesystem, which is where the deep agent can strategically search through its notes on how to search through the data for stage 2. I used a virtual filesystem using the built-in routing functionality (`CompositeBackend`) where I could route the agent to search through the notes before starting the SQL tools. I could guide the agent through the filesystem by using my prompt. I did this by telling it to look into different `.md` files specified for certain types of questions. It is similar to skills, but a bit more deterministic. This by itself increased my accuracy up from 50% to around 70%. I could use my coding agent alongside the evaluations to look through my tool output and analyze how to update this filestorage system.

## Latency

However, a few things were still incorrect. First, I had a latency issue. I was calling way too many tools. Some results were using 15+ tool calls and taking 2 minutes to answer. I used a trick from https://www.anthropic.com/engineering/multi-agent-research-system. Agents struggle to evaluate effort. In my prompt I give a range for how many tool calls to expect: 2-3 for my filesystem traversal, 2-3 usually for SQL tools, somewhere in this range. This drastically improved my average latency from 100-200 seconds to 30 seconds while maintaining a high accuracy. I also realized I didn't really need the to-do tool. The tasks were not large enough to justify using this.

## Streaming

Another issue which I resolved was streaming. Prior, I had a simple streaming system set up. I use a `"Thinking..."` placeholder while the agent output was computing. Then when it finished, the answer would replace the placeholder. I wanted to improve the user experience by adding different types of placeholders depending on what the agent was doing. I separated it into 4 categories:

1. When the user first asks a question, we start with `"thinking..."`.
2. When the agent is searching through the filesystem, we oscillate between placeholders like `"looking through my notes"`, etc.
3. When the agent is calling SQL commands, we include placeholders like `"looking through the database"`.
4. We end with the agent output.

In order to have this streaming setup, I included a basic middleware which checks my tool calls. If the tool calls are in the list associated with filestorage traversal, we are looking through notes. If it is associated with SQL tools, we change the placeholder.

## Large SQL Outputs

Ok great, so now I improved the UI experience, latency, and accuracy for the most part, but there was still one annoying bottleneck. The execute SQL tool was sometimes producing huge outputs which clogged my context window with the tool call result. I initially tried to solve this by truncating, but I ran into a huge issue: it was wiping part of the correct answer from the tool result so the agent could never answer a specific type of question correctly. I got around this error by writing to ephemeral memory using the filesystem. I wrote to the backend under the folder `/large_sql/...` with a random file name and a pointer to that file, along with some instructions. I said in my tool result to strategically use `grep` and `read_file` to read parts of the output without reading the whole thing. This way, the agent could search for aspects within the file. This was the missing piece which took me to near 90+% accuracy on all my questions.

## Conclusion

So in conclusion, I went from ~50-60% accuracy, which is useless in my opinion, to ~90%, which means it almost always picks up the right answer now, and when it is wrong it is usually due to adding too much detail or something minor.

In the future, I want to improve the prompt and notes such that the agent is better at working both when it has long context already included and when we start fresh. But either way, this is now my complete version of `slack-bot-2`!
