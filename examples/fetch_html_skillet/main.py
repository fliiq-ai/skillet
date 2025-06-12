import httpx, asyncio, markdownify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_LEN = 10_000           # keep responses small for token limits

async def handler(params: dict) -> dict:
    """
    params:
      url: str                     (required)
      as_markdown: bool = False    (optional)
      start_index: int  = 0        (optional)
    """
    try:
    url = params["url"]
        as_md = params.get("as_markdown", False)
        start_index = max(0, int(params.get("start_index", 0) or 0))
        
        logger.info(f"Fetching URL: {url}, as_markdown: {as_md}, start_index: {start_index}")
        
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            r = await client.get(url)
        r.raise_for_status()
            content = r.text
            
        logger.info(f"Received content length: {len(content)}")
        
        # paging
        chunk = content[start_index : start_index + MAX_LEN]
        logger.info(f"Chunk length: {len(chunk)}")
        
        if as_md:
            md_chunk = markdownify.markdownify(chunk)
            logger.info("Converted to markdown")
            return {"html": None, "markdown": md_chunk}
        else:
            return {"html": chunk, "markdown": None}
        
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        raise

# Local debug
if __name__ == "__main__":
    print(asyncio.run(handler({"url": "https://example.com"})))
