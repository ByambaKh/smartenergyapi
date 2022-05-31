# coding=utf-8
__author__ = 'L'
STATUS_CHOICES = (
   ('0', 'Идэвхигүй'),
   ('1', 'Идэвхитэй'),
)

FILE_TYPE = (
    ('0', 'NONE'),
    ('1', 'PDF'),
    ('2', 'JPEG'),
    ('3', 'PNG'),
    ('4', 'ZIP'),
)

FILE_CHOOSE_TYPE = (
    ('0', 'Бүгд'),
    ('1', 'PDF'),
    ('2', 'ЗУРАГ'),
)

TARIFF = (
    ('0', 'Өдөр'),
    ('1', 'Шөнө'),
    ('2', 'Оргил цаг'),
)

STATUS = (
    ('0', 'Ашиглагдаагүй'),
    ('1', 'Ашиглагдаж байгаа'),
    ('2', 'Ашиглалтаас гарсан'),
)

TOOLUUR_ANGILAL = (
    ('0', 'Дэд станц'),
    ('1', 'Ахуйн хэрэглэгч'),
)

TRANFORMATOR_TYPE = (
    ('0', 'Гүйдлийн'),
    ('1', 'Хүчдэлийн'),
)

BICHILT_TYPE = (
    ('0', 'Бичилт оруулсан'),
    ('1', 'Баланс тооцсон'),
    ('2', 'Авлага үүссэн'),
)

BICHILT_PROBLEM = (
    ('0', 'Асуудалгүй'),
    ('1', 'Асуудалтай'),
)

UNE_TYPE = (
    ('0', 'Ахуйн хэрэглэгч'),
    ('1', 'Аж ахуйн нэгж'),
    ('2', 'Үйлдвэр үйлчилгээ'),
    ('3', 'Нийтийн эзэмшил'),
)

BUS_TYPE = (
    ('0', 'Өмнөд'),
    ('1', 'Хойд'),
    ('2', 'Баруун'),
    ('3', 'Зүүн'),
    ('4', 'Төв'),
)

TARIFF_TYPE = (
    ('0', 'Нэг'),
    ('1', 'Хоёр'),
    ('2', 'Гурав'),
)

TUL_TYPE = (
    ('0', 'Аж ахуйн нэгж'),
    ('1', 'Хотхон'),
)

SALGALT = (
    ('0', 'Салгалт хийх хүсэлт'),
    ('1', 'Салгасан'),
    ('2', 'Солих хүсэлт'),
    ('3', 'Залгасан'),
)

BICHILT_TYPE = (
    ('0', 'Бичилт оруулсан'),
    ('1', 'Баланс тооцсон'),
    ('2', 'Авлага үүссэн'),
)

UNE_TYPE = (
    ('0', 'Ахуйн хэрэглэгч'),
    ('1', 'Аж ахуйн нэгж'),
    ('2', 'Үйлдвэр үйлчилгээ'),
    ('3', 'Нийтийн эзэмшил'),
)

BUS_TYPE = (
    ('0', 'Өмнөд'),
    ('1', 'Хойд'),
    ('2', 'Баруун'),
    ('3', 'Зүүн'),
    ('4', 'Төв'),
)

TARIFF_TYPE = (
    ('0', 'Нэг'),
    ('1', 'Хоёр'),
    ('2', 'Гурав'),
)

TUL_TYPE = (
    ('0', 'Аж ахуйн нэгж'),
    ('1', 'Хотхон'),
)

SALGALT = (
    ('0', 'Салгалт хийх хүсэлт'),
    ('1', 'Салгасан'),
    ('2', 'Залгах хүсэлт'),
    ('3', 'Залгасан'),
)

PAY_TYPE = (
    ('0', 'Төлөөгүй'),
    ('1', 'Дутуу төлсөн'),
    ('2', 'Төлсөн'),
)

BICHILT_USER_TYPE = (
    ('1', 'Ахуй хэрэглэгч'),
    ('0', 'Дэд станц'),
    ('2', 'Байр'),
)

OUT_OF_DATE = (
    ('0', 'Хугацаа хэтрээгүй'),
    ('1', 'Хугацаа хэтэрсэн'),
)

USE_CHOICES = (
   ('0', 'Ашигласан'),
   ('1', 'Ашиглаагүй'),
)

FILE_USAGE_TYPE = (
    ('0', 'Гэрээ'),
    ('1', 'Техникийн нөхцөл'),
    ('2', 'Тоолуур'),
    ('3', 'Ашиглалт'),
)

TOOLUUR_FLOW_TYPE = (
   ('0', 'Оролт'),
   ('1', 'Гаралт'),
   ('2', 'Дотоод хэрэгцээ'),
   ('3', 'T'),
)

TOOLUUR_INPUT_TYPE = (
   ('0', '10000 kВт'),
   ('1', '0.4 кВт'),
)

CUSTOMER_TYPE = (
   ('0', 'Ахуйн хэрэглэгч'),
   ('1', 'Аж ахуй нэгж'),

)

SHUGAM_TYPE = (
    ('0', 'Залгаатай'),
    ('1', 'Тасархай'),
    ('2', 'Бэлтгэлт'),
)

SHUGAM_TIP_TYPE = (
    ('0', 'Оролт'),
    ('1', 'Гаралт'),
    ('2', 'СХВТ'),
    ('3', 'СХС'),
    ('4', 'ДХТ'),
)

MEDEELEH_ZAGVAR_TYPE = (
    ('0', 'SMS'),
    ('1', 'EMAIL'),
    ('2', 'PRINT'),
)

POWER_TRANS_TYPE = (
    ('0', 'Хуурай'),
    ('1', 'Тосон'),
)

AJIL_GORIM = (
    ('0', 'Өдөр'),
    ('1', 'Шөнө'),
    ('2', '24 цагаар'),
)

TSEH_TULBUR_TYPE = (
    ('0', 'Бэлнээр'),
    ('1', 'Дансаар'),
)

AJILLASAN_HAMGAALALT = (
    ('0', 'Ихсэх гүйдлийн хамгаалалт шууд(MTO Отсечка)'),
    ('1', 'Ихсэх гүйдлийн хамгаалалт хугацаатай (МТЗ)'),
    ('2', 'Газардлагын хамгаалалт'),
    ('3', 'Нумын хамгаалалт'),
    ('4', 'Трансформаторын хамгаалалт'),
    ('5', 'Давтамжийн хамгаалалт (АЧР)'),
)

SHUURHAI_AJILLAGAA = (
    ('0', 'Танилцаагүй'),
    ('1', 'Танилцсан'),
)

FINAL_BALANCE_STATUS_TYPE = (
    ('0', 'Нээлттэй'),
    ('1', 'Хаасан'),
)