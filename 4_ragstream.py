import streamlit as st
from langchain_classic.embeddings import OpenAIEmbeddings
from langchain_classic.vectorstores import Chroma
import os


def load_documents(file):
    import os
    name, extension = os.path.splitext(file)

    if extension == '.pdf':
        from langchain_classic.document_loaders import PyPDFLoader
        print(f'Loading...{file}')
        loader = PyPDFLoader(file)
    elif extension == '.docx':
        from langchain_classic.document_loaders import Docx2txtLoader
        print(f'Loading...{file}')
        loader = Docx2txtLoader(file)
    elif extension == '.txt':
        from langchain_classic.document_loaders import TextLoader
        print(f'Loading...{file}')
        loader = TextLoader(file)
    else:
        print('Document format is not supported.')
        return None

    data=loader.load()
    return data

def chunk_data(data, chunk_size=256, chunk_overlap=20):
    from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
    text_split = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_split.split_documents(data)
    return chunks 

def create_embeddings(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(chunks, embeddings)
    return vectorstore


def get_answer(vector_store, question, k=3):
    from langchain_classic.chains import RetrievalQA
    from langchain_openai.chat_models import ChatOpenAI
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5)
    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k':k})
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
    answer = chain.invoke(question)
    return answer

def calculate_embedding_cost(texts):
    import tiktoken
    enc = tiktoken.encoding_for_model('text-embedding-3-small')
    total_tokens = sum([len(enc.encode(page.page_content)) for page in texts])
    print(f'Total tokens {total_tokens}')
    print(f'Embedding cost in US$: {total_tokens/1000 *0.0004:.6f}')

#call back function to clear the chat history
def clear_chat_history():
    if 'history' in st.session_state:
        del st.session_state['history']

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)

    st.image('img.png')
    st.subheader('LLM Document Question Answering')
    with st.sidebar:
        api_key = st.text_input('Enter your OpenAI API key', type='password')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key

        uploaded_file = st.file_uploader('Upload your document', type=['pdf', 'docx', 'txt'])
        chunk_size = st.number_input('Chunk size', min_value=64, max_value=1024, value=256, step=64, on_change=clear_chat_history)
        k = st.number_input('k', min_value=1, max_value=10, value=3, on_change=clear_chat_history)
        add_data = st.button('Add data', on_click=clear_chat_history)

        if uploaded_file and add_data:
            with st.spinner('Reading, chunking and embeded file...'):
                bytes_data = uploaded_file.read()
                file_name  = os.path.join('./', uploaded_file.name)
                with open(file_name, 'wb') as f:
                    f.write(bytes_data)

                data = load_documents(file_name)
                chunks = chunk_data(data, chunk_size=chunk_size)
                st.write(f'chunk size:{chunk_size}, {len(chunks)}')

                tokens, embedding_cost = calculate_embedding_cost(chunks)
                st.write(f'Embedding cost: ${embedding_cost:.4f}')

                vector_store = create_embeddings(chunks)
                st.session_state.vs = vector_store  
                st.success('File uploaded, chunked and embedded successfully!')

    quest = st.text_input("Ask a question about the content of your file")
    if quest:
        if 'vs' in st.session_state:
            vector_store = st.session_state.vs
            st.write(f'k: {k}')
            answer = get_answer(vector_store, quest, k=k)
            st.text_area('Answer', value=answer['result'], height=200)
        else:
            st.warning('Please upload a document first.')

        st.divider()    
        if 'history' not in st.session_state:
            st.session_state.history = []
        value=f'Q: {quest}\nA: {answer["result"]}' 
        st.session_state.history = f'{value} \n {'-'*100} \n {st.session_state.history}'
        h = st.session_state.history
        st.text_area(label='Chat History', value=h, key='history', height=400)











