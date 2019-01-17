from mongoengine import *

from projects.trains.models import Train

connect(db='trains', host='localhost', port=27017)

'''
ensure mongodb server is running with
C:\Program Files\MongoDB\Server\4.0\bin\mongod.exe
'''

class TrainDocument(Document):
    meta={'collection': 'train'}

    service_id = StringField(required=True)
    service = DictField()
    details = DictField()

    @classmethod
    def from_dataclass(cls, model: Train):
        return cls(
            service_id=model.service_id,
            service=model.service,
            details=model.details,
        )

    def to_dataclass(self) -> Train:
        return Train(
            service=self.service,
            service_id=self.service_id,
            details=self.details,
        )


def save_observation(train_model: Train):
    doc = TrainDocument.from_dataclass(train_model)
    print(doc)
    doc.save()


def get_observation_by_id(train_id: str) -> Train:
    pass

pass