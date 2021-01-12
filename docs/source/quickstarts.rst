===========
Quickstarts
===========

Installation
~~~~~~~~~~~~

.. include:: installation.rst
    :start-line: 4

Usage
~~~~~

.. code-block:: python3

    from data_extractor import Field, Item, JSONExtractor


    class Count(Item):
        followings = Field(JSONExtractor("countFollowings"))
        fans = Field(JSONExtractor("countFans"))


    class User(Item):
        name_ = Field(JSONExtractor("name"), name="name")
        age = Field(JSONExtractor("age"), default=17)
        count = Count()


    assert User(JSONExtractor("data.users[*]"), is_many=True).extract(
        {
            "data": {
                "users": [
                    {"name": "john", "age": 19, "countFollowings": 14, "countFans": 212,},
                    {
                        "name": "jack",
                        "description": "",
                        "countFollowings": 54,
                        "countFans": 312,
                    },
                ]
            }
        }
    ) == [
        {"name": "john", "age": 19, "count": {"followings": 14, "fans": 212}},
        {"name": "jack", "age": 17, "count": {"followings": 54, "fans": 312}},
    ]
