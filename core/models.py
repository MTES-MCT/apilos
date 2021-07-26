from django.db import models

class IngestableModel(models.Model):
    pivot= ''
    mapping= {}

    class Meta:
        abstract = True

    @classmethod
    def map_and_create(cls, elements):
        mapped_elements = {}
        for element in elements:
            element_pivot = element[cls.mapping[cls.pivot]]
            if not element_pivot in mapped_elements:
                print(element_pivot)
                mapped_elements[element_pivot] = {}
                for element_item in cls.mapping.items():
                    mapped_elements[element_pivot][element_item[0]] = element[element_item[1]]
                cls.find_or_create_by_pivot(mapped_elements[element_pivot])
        return mapped_elements

    @classmethod
    def find_or_create_by_pivot(cls, element):
        object_filter = {cls.pivot: element[cls.pivot]}
        if not cls.objects.filter(**object_filter):
            new_object = cls(**element)
            new_object.save()
        else:
            print('already exist!')
