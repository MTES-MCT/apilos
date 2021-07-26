from django.db import models

def build_filter(my_cls, element_dict):
    object_filter = {}
    if isinstance(my_cls.pivot,list):
        for pivot in my_cls.pivot:
            if type(my_cls._meta.get_field(pivot)).__name__ == 'ForeignKey':
                sub_object_filter = build_filter(
                my_cls._meta.get_field(pivot).related_model,
                element_dict)
                object_filter[my_cls._meta.get_field(pivot).attname] = my_cls._meta.get_field(
                pivot
                ).related_model.objects.filter(**sub_object_filter)[0].id
            else:
                object_filter[pivot] = element_dict[my_cls.mapping[pivot]]
    else:
        object_filter = {my_cls.pivot: element_dict[my_cls.mapping[my_cls.pivot]]}
    return object_filter

class IngestableModel(models.Model):
    pivot= ''
    mapping= {}

    class Meta:
        abstract = True

    @classmethod
    def map_and_create(cls, elements):
        count = 0
        mapped_elements = {}
        for element in elements:
            # pylint: disable=W0640, cell-var-from-loop
            element_pivot = "__".join(
            map(lambda pivot: element[cls.mapping[pivot]], cls.pivot)
            ) if isinstance(cls.pivot,list) else element[cls.mapping[cls.pivot]]
            if not element_pivot in mapped_elements:
#                print(element_pivot)
                mapped_elements[element_pivot] = {}
                for element_item in cls.mapping.items():
                    mapped_elements[element_pivot][element_item[0]] = element[element_item[1]]
                if cls.find_or_create_by_pivot(mapped_elements[element_pivot], element):
                    count += 1
        print(f"{count} éléments créés de class {cls}")
        return mapped_elements

    @classmethod
    def find_or_create_by_pivot(cls, element, full_element):
        object_filter = build_filter(cls, full_element)
        if not cls.objects.filter(**object_filter):
            object_fields = {}
            for each_field in element.keys():
                if type(cls._meta.get_field(each_field)).__name__ == 'ForeignKey':
                    sub_object_filter = build_filter(
                    cls._meta.get_field(each_field).related_model, full_element)
                    object_fields[each_field] = cls._meta.get_field(
                    each_field
                    ).related_model.objects.filter(**sub_object_filter)[0]
                else:
                    if type(cls._meta.get_field(each_field)).__name__ == 'CharField':
                        object_fields[each_field] = element[each_field]
                    else:
                        object_fields[each_field] = element[each_field]
            new_object = cls(**object_fields)
            new_object.save()
        else:
#            print('already exist!')
            return False
        return True
