from modeltranslation.translator import TranslationOptions, translator
from .models import Post, Category


class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Post, PostTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
