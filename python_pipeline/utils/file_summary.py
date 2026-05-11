

def generate_file_level(chunks_with_summary,call_graph,dependency_graph):
# add token support for embedding model
# decide on the resultant schema after combining chunks_with_summary,call_graph,dependency_graph
# add token count in call graph, dep graph,chunk_summary (only required fields token)
## group summaries by filename
    # from itertools import groupby

    # sorted_summaries = sorted(response.summaries, key=lambda x: x.filename)
    # for filename, chunks in groupby(sorted_summaries, key=lambda x: x.filename):
    #     file_chunks = list(chunks)
    # generate file summary from file_chunks