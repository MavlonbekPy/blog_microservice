from modeltranslation.translator import translator, TranslationOptions
from .models import Post, Category, Tag


class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


class TagTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Post, PostTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(Tag, TagTranslationOptions)
