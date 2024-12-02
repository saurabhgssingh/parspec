# prompt: write a async function to get download and save all urls

import asyncio
import aiohttp
import pandas as pd
import os

data_path = "data/train"
df = pd.read_excel("DataSet.xlsx",sheet_name="train_data")


# We will save the PDFs with the index name so that it is easy to map back to the labels

# some links dont have https hence adding https
df.datasheet_link = df.datasheet_link.apply(lambda x: "https:" + x if not x.startswith("http") else x)

# adding a header signature to allow download requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}


failed_urls = []
async def download_and_save(session, url, filename):
    """Downloads a file from a URL and saves it to a specified path."""
    try:
        async with session.get(url,headers=headers) as response:
            if response.status == 200:
                with open(filename, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
                return True  # Indicate successful download
            else:
                print(f"Error downloading {url}: Status code {response.status}")
                print(filename)
                failed_urls.append(url)
                return False # Indicate download failure
    except aiohttp.ClientError as e:
        print(f"Error downloading {url}: {e}")
        return False # Indicate download failure

async def process_urls(df):
    """Processes a DataFrame of URLs, downloads files, and extracts text."""

    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, row in df.iterrows():
            url = row['datasheet_link']
            filename = str(index) + "_" + ".pdf" 
            filename = os.path.join(data_path,filename)
            tasks.append(download_and_save(session, url, filename))
        results = await asyncio.gather(*tasks)
    return results

# Example usage (assuming 'df' is your DataFrame)
async def main():
    # Assuming df is your DataFrame
    success_results = await process_urls(df)

    print(f"Download Results: {success_results}")
    
    # Optionally, add code here to proceed with extracted_text from files

if __name__ == "__main__":
    asyncio.run(main())
    with open("failed.txt","w") as f:
        f.write(str(failed_urls))