# GPT-Based Knowledge Base for YouTube Videos


## Objective
- Construct a local knowledge base using existing datasets
- Enable natural language queries for searching content within the knowledge base
- Provide natural language responses based on query results


## Implementation

![9dTKpRlhtF6CkSz](https://s2.loli.net/2023/03/14/9dTKpRlhtF6CkSz.jpg)

### prefix prompt

```json
[
    {
        "role": "system",
        "content": "I am a highly proficient QA bot capable of providing precise answers from the available document repository. I can frame my responses using the provided text, preferring to paraphrase when possible, rather than copying verbatim. My responses are accurate, helpful, concise, and clear."
    },
    {
        "role": "user",
        "content": "My query is: [XXXXX]. Please provide the answer using the following text sections: \n1.[Vector Query Result top1]\n2.[Vector Query Result top2]\n..."
    }
]

```

### example

![K7NHrZYxsyuzmiq](https://s2.loli.net/2023/03/14/K7NHrZYxsyuzmiq.png)

## System Requirements and Installation


1. Database: postgreSQL + pgvector
2. Python 3.8+
3. Fast whisper model

```bash
pip3 install -r requirements.txt
```
To download a YouTube list or video and save the embedding into postgreSQL, run:

    python main.py --url 'https://youtube_list_or_video_url'

To perform a query, run:

    python main.py --query

## Reference

* [faster whisper](https://github.com/guillaumekln/faster-whisper)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* [knowledge-base-with-gpt](https://github.com/vsxd/knowledge-base-with-gpt)