# """
# Web document loader using LangChain's WebBaseLoader.
# """

# import bs4
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_core.documents import Document


# def load_web_documents(
#     urls: list[str] | str,
#     css_classes: tuple[str, ...] | None = None,
# ) -> list[Document]:
#     """
#     Load documents from web URLs.
    
#     Args:
#         urls: Single URL or list of URLs to load
#         css_classes: Optional tuple of CSS classes to filter content.
#                      If None, loads entire page content.
    
#     Returns:
#         List of Document objects
        
#     Example:
#         docs = load_web_documents(
#             "https://lilianweng.github.io/posts/2023-06-23-agent/",
#             css_classes=("post-title", "post-header", "post-content")
#         )
#     """
#     if isinstance(urls, str):
#         urls = [urls]
    
#     bs_kwargs = {}
#     if css_classes:
#         bs_kwargs["parse_only"] = bs4.SoupStrainer(class_=css_classes)
    
#     loader = WebBaseLoader(
#         web_paths=urls,
#         bs_kwargs=bs_kwargs if bs_kwargs else None,
#     )
    
#     return loader.load()
