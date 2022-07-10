from django.db import models
from django.forms.models import model_to_dict


def object_exists(cls, **kwargs):
    return cls.objects.filter(**kwargs).exists()


class Tag(models.Model):
    name = models.TextField()
    recipes = models.ManyToManyRel('', to='tags')

    @classmethod
    def exists(cls, **kwargs):
        return object_exists(cls, **kwargs)

    @classmethod
    def all_by_recipe_count(cls):
        return sorted([r for r in cls.objects.all() if r.recipes.count()], key=lambda x: x.recipes.count(), reverse=True)

    @classmethod
    def all_by_name(cls):
        return cls.objects.order_by('name').all()

    def __str__(self):
        return self.name

    def as_dict(self):
        ret = model_to_dict(self)

        return ret


class Recipe(models.Model):
    name = models.TextField(default='')
    link = models.TextField(default='')
    tags = models.ManyToManyField(Tag, related_name='recipes')

    def __str__(self):
        return self.name

    @classmethod
    def exists(cls, **kwargs):
        return object_exists(cls, **kwargs)

    @classmethod
    def all_untagged(cls):
        return [x for x in cls.objects.order_by('name').all() if not x.tags.count()]

    @classmethod
    def all_by_name(cls):
        return cls.objects.order_by('name').all()

    def as_dict(self):
        ret = model_to_dict(self)

        ret['tags'] = [t.as_dict() for t in self.tags.all()]

        return ret
