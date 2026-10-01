from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["text"]
    text: str = Field(max_length=20000)


class ImageBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["image"]
    image_url: str = Field(pattern=r"^/static/uploads/about/[a-f0-9]{32}\.(jpg|png|webp)$")
    caption: str = Field(default="", max_length=500)
    alt: str = Field(default="", max_length=300)


class AboutUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    blocks: list[Annotated[TextBlock | ImageBlock, Field(discriminator="type")]] = Field(max_length=50)


class AboutResponse(AboutUpdate):
    configured: bool = False
