from pydantic import BaseModel


class Pagination:

    class Page(BaseModel):
        total_page: int
        total_count: int
        current_page: int

    def get_page_data(self, total_count, page_count, current_page):
        total_page = total_count // page_count if total_count % page_count == 0 else total_count // page_count + 1
        return self.Page(
            total_page=total_page,
            total_count=total_count,
            current_page=current_page
        )

pagination = Pagination()