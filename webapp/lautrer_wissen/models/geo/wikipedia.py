# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.db.models.functions import Length
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.db.models import Case, When
from ..base_model import BaseModel
from ..mixins import FrontendURLMixin
import django
import re
import hashlib


class WikiModel(BaseModel, FrontendURLMixin):

    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS,
    }

    DB_CASE_MODIFY_NAME = Case(
        When(
            name__in=[
                "Wohnhaus",
                "Wohnhäuser",
                "Gasthaus",
                "Wohn- und Geschäftshaus",
                "Wohn- und Geschäftshäuser",
                "Villa",
                "Stadtbefestigung",
                "Kriegerdenkmal",
            ],
            then=Concat(
                F("name"),
                Value(" ("),
                F("address"),
                Value(")"),
                output_field=CharField(),
            ),
        ),
        default=F("name"),
        output_field=CharField(),  # Ensure the output is consistently CharField
    )

    class Meta:
        abstract = True  # This makes it an abstract base class in Django

    @property
    def virtual_id(self):
        # Create a hash from lat/lon
        lat = self.geometry.y
        lon = self.geometry.x
        return hashlib.md5(f"{lat}:{lon}".encode()).hexdigest()

    @classmethod
    def objects_for_list_view(cls):
        objs = (
            cls.objects.annotate(has_image=Length("image_url"))
            .annotate(combined_name=WikiModel.DB_CASE_MODIFY_NAME)
            .order_by("-has_image", "name")
        )
        return objs

    @classmethod
    def nearby_objects_as_dict(cls, curr_obj, top_n=5):
        return [
            {
                "distance": str(round(obj.distance.km, 3)).replace(".", ","),
                "id": obj.virtual_id,
                "name": obj.combined_name,
            }
            for obj in cls._nearby_objects_by_location(curr_obj, top_n)
        ]

    @classmethod
    def _nearby_objects_by_location(cls, curr_obj, top_n=5):
        return (
            cls.objects.annotate(distance=Distance("geometry", curr_obj.geometry))
            .annotate(combined_name=WikiModel.DB_CASE_MODIFY_NAME)
            .order_by("distance")[1 : top_n + 1]
        )

    geometry = models.PointField()
    image_url = models.TextField(default="")
    image_license_url = models.TextField(default="")
    image_license_text = models.TextField(default="")
    image_author_name = models.TextField(default="")
    reference_names = models.TextField(default="")
    reference_links = models.TextField(default="")
    image_additional_urls = models.TextField(default="")
    image_additional_author_names = models.TextField(default="")
    image_additional_license_urls = models.TextField(default="")
    image_additional_license_texts = models.TextField(default="")

    def get_references(self):
        return [
            {"ref": ref, "link": link}
            for ref, link in zip(
                self.reference_names.split(";")[:-1],
                self.reference_links.split(";")[:-1],
            )
        ]

    def get_image_info(self):
        """Returns the image info of the object."""
        res = {
            "image_url": (
                re.sub(r"/(\d+)px", "/500px", str(self.image_url))
                if self.image_url
                else ""
            ),
            "image_author_name": self.image_author_name,
            "image_license_url": self.image_license_url,
            "image_license_text": self.image_license_text,
        }

        if self.image_additional_urls:
            image_additional_urls = re.sub(
                r"/(\d+)px", "/500px", str(self.image_additional_urls)
            )
            image_additional_urls = image_additional_urls.split(";")[:-1]
            image_additional_author_names = str(
                self.image_additional_author_names
            ).split(";")[:-1]
            image_additional_license_urls = str(
                self.image_additional_license_urls
            ).split(";")[:-1]
            image_additional_license_texts = str(
                self.image_additional_license_texts
            ).split(";")[:-1]

            res["image_additional_info"] = [
                {"url": url, "author_name": an, "license_url": lu, "license_text": lt}
                for url, an, lu, lt in zip(
                    image_additional_urls,
                    image_additional_author_names,
                    image_additional_license_urls,
                    image_additional_license_texts,
                )
            ]
        return res


class WikiFishSculpture(WikiModel):

    WIKI_OBJECT_URL = "https://de.wikipedia.org/wiki/Liste_der_%C3%B6ffentlichen_Fischskulpturen_in_Kaiserslautern"
    VISIBLE_OBJECT_NAME = "Fischskulptur"
    MAP_FIELDS = {
        "name": "Name",
        "number": "Nummer",
        "address": "Adresse",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    designed_by = models.TextField()
    address_past = models.TextField()
    number = models.IntegerField()

    def get_references(self):
        return []  # No references for fish sculptures

    def get_image_info(self):
        return {
            "image_url": (
                re.sub(r"/(\d+)px", "/480px", str(self.image_url))
                if self.image_url
                else ""
            ),
            "image_author_name": self.image_author_name,
            "image_license_url": self.image_license_url,
            "image_license_text": self.image_license_text,
        }

    def get_fields_to_display(self):
        res = {
            "Name": self.name,
            "Adresse": self.address if self.address else "Unbekannt",
            "Gestaltet von": self.designed_by if self.designed_by else "Unbekannt",
        }
        if self.number != -1:
            res["Nummer"] = self.number
        return res



class WikiCulturalMonument(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_der_Kulturdenkmäler_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Kulturdenkmal"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Beschreibung",
        "address": "Adresse",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()
    construction_year = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Baujahr": self.construction_year,
            "Beschreibung": str(self.description).replace(" .", "."),
            "Adresse": self.address if self.address else "Unbekannt",
        }


class WikiNaturalMonument(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_der_Naturdenkmale_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Naturdenkmal"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Beschreibung",
        "address": "Adresse",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()
    id_no = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Beschreibung": str(self.description).replace(" .", "."),
            "Adresse": self.address if self.address else "Unbekannt",
        }


class WikiFountain(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Brunnen"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Beschreibung",
        "address": "Adresse",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Beschreibung": str(self.description).replace(" .", "."),
            "Adresse": self.address if self.address else "Unbekannt",
        }


class WikiBrewery(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Ehemalige Brauerei"
    MAP_FIELDS = {
        "name": "Name",
        "address": "Lage",
        "timespan": "Betrieb",
        "description": "Beschreibung",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()
    timespan = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Lage": self.address,
            "Betrieb": self.timespan,
            "Beschreibung": str(self.description).replace(" .", "."),
        }


class WikiNaturalReserve(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Naturschutzgebiet"
    MAP_FIELDS = {
        "name": "Name",
        "identifier": "Kennung",
        "location_area": "Kreis (Lage)",
        "date": "Datum",
        "area": "Fläche [ha]",
        "details": "Einzelheiten",
        **BaseModel.MAP_FIELDS,
    }
    name = models.TextField()
    location_area = models.TextField()
    details = models.TextField()
    area = models.TextField()
    date = models.TextField()
    identifier = models.TextField()

    DB_CASE_MODIFY_NAME = Case(
        When(
            name__in=[
                "Wohnhaus",
                "Wohnhäuser",
                "Gasthaus",
                "Wohn- und Geschäftshaus",
                "Wohn- und Geschäftshäuser",
                "Villa",
                "Stadtbefestigung",
                "Kriegerdenkmal",
            ],
            then=Concat(F("name"), Value(" ("), Value(")"), output_field=CharField()),
        ),
        default=F("name"),
        output_field=CharField(),  # Ensure the output is consistently CharField
    )

    @classmethod
    def objects_for_list_view(cls):
        objs = (
            cls.objects.annotate(has_image=Length("image_url"))
            .annotate(combined_name=WikiNaturalReserve.DB_CASE_MODIFY_NAME)
            .order_by("-has_image", "name")
        )
        return objs

    @classmethod
    def _nearby_objects_by_location(cls, curr_obj, top_n=5):
        return (
            cls.objects.annotate(distance=Distance("geometry", curr_obj.geometry))
            .annotate(combined_name=WikiNaturalReserve.DB_CASE_MODIFY_NAME)
            .order_by("distance")[1 : top_n + 1]
        )

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Kennung": self.identifier,
            "Kreis (Lage)": self.location_area,
            "Datum": self.date,
            "Fläche [ha]": self.area,
            "Einzelheiten": self.details,
        }


class WikiRitterstein(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Ritterstein"
    MAP_FIELDS = {
        "name": "Name",
        "meaning": "Bedeutung",
        "number": "Nummer",
        "address": "Beschreibung der Lage",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    meaning = models.TextField()
    number = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Nummer": self.number,
            "Bedeutung": self.meaning,
            "Beschreibung der Lage": self.address,
        }


class WikiSacralBuilding(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Sakralbau"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Anmerkungen",
        "construction_year": "Bauzeit",
        "address": "Stadtteil/Lage",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()
    construction_year = models.TextField()

    def get_fields_to_display(self):
        return {
            "Name": self.name,
            "Anmerkungen": self.description,
            "Bauzeit": self.construction_year,
            "Stadtteil/Lage": self.address,
        }


class WikiStolperstein(WikiModel):
    WIKI_OBJECT_URL = (
        "https://de.wikipedia.org/wiki/Liste_von_Brunnen_in_Kaiserslautern"
    )
    VISIBLE_OBJECT_NAME = "Stolperstein"
    MAP_FIELDS = {
        "name": "Person, Inschrift",
        "description": "Beschreibung",
        "timespan": "Verlegedatum",
        "address": "Verlegeort",
        **BaseModel.MAP_FIELDS,
    }
    address = models.TextField()
    name = models.TextField()
    description = models.TextField()
    timespan = models.TextField()

    def get_fields_to_display(self):
        same_location_qs = (
            self.__class__.objects
            .filter(geometry=self.geometry)
            .exclude(pk=self.pk)   # exclude current object
        )
        if same_location_qs.exists():
            names = [self.name] + list(same_location_qs.values_list("name", flat=True))
            combined_names = "  //  ".join(names)
        else:
            combined_names = self.name

        return {
            "Person, Inschrift": combined_names,
            "Beschreibung": self.description,
            "Verlegedatum": self.timespan,
            "Verlegeort": self.address,
        }
    
    def get_image_info(self):
        """Returns the image info of the object and any others at the same location."""

        # helper to normalize URL
        def normalize_url(url):
            return re.sub(r"/(\d+)px", "/500px", str(url)) if url else ""

        # base object image info
        res = {
            "image_url": normalize_url(self.image_url),
            "image_author_name": self.image_author_name,
            "image_license_url": self.image_license_url,
            "image_license_text": self.image_license_text,
        }

        # collect additional images from other objects with the same geometry
        same_location_qs = (
            self.__class__.objects
            .filter(geometry=self.geometry)
            .exclude(image_url__isnull=True)
            .exclude(image_url__exact="")
        )

        additional_info = []
        for obj in same_location_qs:
            additional_info.append({
                "url": normalize_url(obj.image_url),
                "author_name": obj.image_author_name,
                "license_url": obj.image_license_url,
                "license_text": obj.image_license_text,
            })

        if additional_info:
            res["image_additional_info"] = additional_info

        return res
    
    @classmethod
    def _nearby_objects_by_location(cls, curr_obj, top_n=5):
        return (
            cls.objects.annotate(distance=Distance("geometry", curr_obj.geometry))
            .annotate(combined_name=WikiModel.DB_CASE_MODIFY_NAME)
            .filter(distance__gt=0)
            .order_by("distance")[1 : top_n + 1]
        )
    

MODEL_CLASSES = [
    WikiFishSculpture,
    WikiFountain,
    WikiCulturalMonument,
    WikiNaturalMonument,
    WikiBrewery,
    WikiNaturalReserve,
    WikiRitterstein,
    WikiSacralBuilding,
    WikiStolperstein,
]
