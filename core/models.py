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

# Résolution récurcive du pivot
def get_elements_for_pivots(cls, element):
    result_pivots = []
    pivots = cls.pivot
    if not isinstance(pivots,list):
        pivots = [pivots]
    for pivot in pivots:
        if type(cls._meta.get_field(pivot)).__name__ == 'ForeignKey':
            subresult = get_elements_for_pivots(cls._meta.get_field(pivot).related_model, element)
            if isinstance(subresult,list):
                result_pivots += subresult
            else:
                result_pivots.append(subresult)
        else:
            result_pivots.append(element[cls.mapping[pivot]])
    return result_pivots


class IngestableModel(models.Model):
    pivot= ''
    mapping= {}

    class Meta:
        abstract = True

    @classmethod
    def map_and_create(cls, elements, create_only=True):
        count = 0
        count_dup = 0
        mapped_elements = {}
        for element in elements:
            # pylint: disable=W0640, cell-var-from-loop
            element_pivot = "__".join(get_elements_for_pivots(cls, element))
            if element_pivot not in mapped_elements:
#                print(element_pivot)
                mapped_elements[element_pivot] = {}
                for element_item in cls.mapping.items():
                    mapped_elements[element_pivot][element_item[0]] = element[element_item[1]]
                if cls.find_or_create_by_pivot(
                mapped_elements[element_pivot], element, create_only):
                    count += 1
            else:
                count_dup += 1
                mapped_elements2 = {}
                for element_item in cls.mapping.items():
                    mapped_elements2[element_item[0]] = element[element_item[1]]
        print(f"{count} éléments créés ou mis à jour de class {cls}")
        print(f"{count_dup} éléments dupliqué pour la class {cls}")
        return mapped_elements

    @classmethod
    def find_or_create_by_pivot(cls, element, full_element, create_only=True):
        object_filter = build_filter(cls, full_element)
        my_objects = cls.objects.filter(**object_filter)
        if not my_objects:
            object_fields = {}
            for each_field in element.keys():
                if type(cls._meta.get_field(each_field)).__name__ == 'ForeignKey':
                    sub_object_filter = build_filter(
                    cls._meta.get_field(each_field).related_model, full_element)
                    object_fields[each_field] = cls._meta.get_field(
                    each_field
                    ).related_model.objects.filter(**sub_object_filter)[0]
                else:
                    object_fields[each_field] = element[each_field]
            new_object = cls(**object_fields)
            new_object.save()
            return True
        if not create_only:
            if len(my_objects) != 1:
                print('multiple object returned, ' +
                f'it is not possible to update it, it is too dangerous {object_filter}')
            else:
                my_object = my_objects[0]
                for each_field in element.keys():
                    if type(cls._meta.get_field(each_field)).__name__ == 'ForeignKey':
                        sub_object_filter = build_filter(
                        cls._meta.get_field(each_field).related_model, full_element)
                        my_object.__setattr__(each_field,cls._meta.get_field(
                        each_field
                        ).related_model.objects.filter(**sub_object_filter)[0])
                    else:
                        my_object.__setattr__(each_field,element[each_field])
                my_object.save()
                return True
        return False
