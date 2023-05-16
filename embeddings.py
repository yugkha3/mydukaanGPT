import os
from bs4 import BeautifulSoup
from langchain.text_splitter import TokenTextSplitter

def extract_data(root_path: str) -> list:
    print(f'Extracting data from webpages at: {root_path}')
    pages = []

    for subdir, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(subdir, file)
                soup = BeautifulSoup(open(path), 'html.parser')
                
                text = soup.get_text()
                if soup.title:
                    title = str(soup.title.string)
                else:
                    title = ""
                url = 'https://help.mydukaan.io' + path[len(root_path):]

                pages.append({
                    'page_content': text + '\n\n',
                    'metadata': {
                        'title': title,
                        'url': url
                    }
                })
    
    print(f'Extracted data from {len(pages)} pages.\n')
    return pages

def split_data(pages: list) -> tuple:
    text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=100)

    docs, metadata = [], []

    for page in pages:
        splits = text_splitter.split_text(page['page_content'])
        docs.extend(splits)
        metadata.extend([{'title': page['metadata']['title'], 'url': page['metadata']['url']}] * len(splits))
        print(f"Splitted {page['metadata']['title']} into {len(splits)} chunks.")

    print('\n')
    return docs, metadata

def main():
    root_path = './help.mydukaan.io'
    pages = extract_data(root_path)

    docs, metadata = split_data(pages)

if __name__ == '__main__':
    main()