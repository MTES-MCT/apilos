from django.db import models
from django.db.utils import DataError


def lower_value_using_mapping(my_cls, element_dict, pivot):
    return element_dict[my_cls.mapping[pivot]].lower()


def check_value_using_mapping(my_cls, element_dict, pivot, value):
    return element_dict[my_cls.mapping[pivot]].lower() == value.lower()


def filter_choices_on_value(my_cls, element_dict, pivot):
    return list(
        filter(
            lambda x: element_dict[my_cls.mapping[pivot]].lower() == x[1].lower(),
            my_cls._meta.get_field(pivot).choices,
        )
    )


def filter_choices_on_key(my_cls, element_dict, key):
    return list(
        filter(
            lambda x: element_dict[key].lower() == x[1].lower(),
            my_cls._meta.get_field(key).choices,
        )
    )


def build_filter(my_cls, element_dict):
    object_filter = {}
    if isinstance(my_cls.pivot, list):
        for pivot in my_cls.pivot:
            if isinstance(
                my_cls._meta.get_field(pivot), models.fields.related.ForeignKey
            ):
                sub_object_filter = build_filter(
                    my_cls._meta.get_field(pivot).related_model, element_dict
                )
                object_filter[my_cls._meta.get_field(pivot).attname] = (
                    my_cls._meta.get_field(pivot)
                    .related_model.objects.filter(**sub_object_filter)[0]
                    .id
                )
            elif (
                isinstance(my_cls._meta.get_field(pivot), models.fields.CharField)
                and my_cls._meta.get_field(pivot).choices
            ):
                filter_on_value = filter_choices_on_value(my_cls, element_dict, pivot)
                if filter_on_value:
                    object_filter[pivot] = filter_on_value[0][0]
                else:
                    object_filter[pivot] = element_dict[my_cls.mapping[pivot]]
            else:
                object_filter[pivot] = element_dict[my_cls.mapping[pivot]]
    else:
        object_filter = {my_cls.pivot: element_dict[my_cls.mapping[my_cls.pivot]]}
    return object_filter


# Résolution récurcive du pivot
def get_elements_for_pivots(my_cls, element):
    result_pivots = []
    pivots = my_cls.pivot
    if not isinstance(pivots, list):
        pivots = [pivots]
    for pivot in pivots:
        if isinstance(my_cls._meta.get_field(pivot), models.fields.related.ForeignKey):
            subresult = get_elements_for_pivots(
                my_cls._meta.get_field(pivot).related_model, element
            )
            if isinstance(subresult, list):
                result_pivots += subresult
            else:
                result_pivots.append(subresult)
        else:
            result_pivots.append(element[my_cls.mapping[pivot]])
    return result_pivots


def _create_object_from_fields(cls, element, full_element):

    object_fields = {}
    for each_field in element.keys():
        if isinstance(
            cls._meta.get_field(each_field), models.fields.related.ForeignKey
        ):
            object_fields[each_field] = cls._meta.get_field(
                each_field
            ).related_model.objects.filter(
                **build_filter(
                    cls._meta.get_field(each_field).related_model, full_element
                )
            )[
                0
            ]
        elif isinstance(cls._meta.get_field(each_field), models.fields.IntegerField):
            try:
                object_fields[each_field] = int(element[each_field])
            except ValueError:
                print(
                    f"IGNORED field {each_field} because value is not"
                    + f" int as required : {element[each_field]}"
                )
        elif (
            isinstance(cls._meta.get_field(each_field), models.fields.CharField)
            and cls._meta.get_field(each_field).choices
        ):
            filter_on_value = filter_choices_on_key(cls, element, each_field)
            if filter_on_value:
                object_fields[each_field] = filter_on_value[0][0]
            else:
                object_fields[each_field] = element[each_field]
        else:  # Manage enum case
            object_fields[each_field] = element[each_field]
    return object_fields


class IngestableModel(models.Model):
    pivot = ""
    mapping = {}

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
                mapped_elements[element_pivot] = {}
                for element_item in cls.mapping.items():
                    mapped_elements[element_pivot][element_item[0]] = element[
                        element_item[1]
                    ]
                if cls.find_or_create_by_pivot(
                    mapped_elements[element_pivot], element, create_only
                ):
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
            object_fields = _create_object_from_fields(cls, element, full_element)
            new_object = cls(**object_fields)
            try:
                new_object.save()
            except DataError:
                print(
                    "[DataError] Error Data while saving object,"
                    + " probably linked to Decimal and false rent amount"
                    + f" {new_object.__dict__}"
                )
                return False
            return True
        if not create_only:
            if len(my_objects) != 1:
                print(
                    "multiple object returned, "
                    + f"it is not possible to update it, it is too dangerous {object_filter}"
                )
            else:
                my_object = my_objects[0]
                for each_field in element.keys():
                    cls._object_assign_resolve_field(
                        my_object, each_field, element, full_element
                    )
                my_object.save()
                return True
        return False

    @classmethod
    def _object_assign_resolve_field(cls, my_object, each_field, element, full_element):
        if isinstance(
            cls._meta.get_field(each_field),
            models.fields.related.ForeignKey,
        ):
            my_object.__setattr__(
                each_field,
                cls._meta.get_field(each_field).related_model.objects.filter(
                    **build_filter(
                        cls._meta.get_field(each_field).related_model,
                        full_element,
                    )
                )[0],
            )

        elif isinstance(cls._meta.get_field(each_field), models.fields.IntegerField):
            try:
                my_object.__setattr__(each_field, int(element[each_field]))
            except ValueError:
                print(
                    f"IGNORED field {each_field} because value is not"
                    + f" int as required : {element[each_field]}"
                )
        elif (
            isinstance(cls._meta.get_field(each_field), models.fields.CharField)
            and cls._meta.get_field(each_field).choices
        ):
            filter_on_value = filter_choices_on_key(cls, element, each_field)
            if filter_on_value:
                my_object.__setattr__(each_field, filter_on_value[0][0])
            else:
                my_object.__setattr__(each_field, element[each_field])
        else:
            my_object.__setattr__(each_field, element[each_field])
