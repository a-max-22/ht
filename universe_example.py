from core.universes import Level, Universe, Type, Constructor, UniversePolymorphism
from core.base_types import unit, Empty, Unit
from core.dependent_types import Sigma, Pi



def configure_pc():
    base_level = Level(0)

    components_level = Level(1)
    components = Universe(components_level)

    configurations_level = Level(2)
    configurations = Universe(configurations_level)

    templates_level = Level(3)
    templates = Universe(templates_level)

    # Шаг 1.  Конструируем  базовые компоненты (universe 1)
    cpu = Type("CPU", base_level, components)

    intel_constructor = Constructor('Some Intel Processor',{})
    elbrus_constructor = Constructor('Some Elbrus Processor',{})

    cpu.add_constructor(intel_constructor.name, intel_constructor)
    cpu.add_constructor(elbrus_constructor.name, elbrus_constructor)

    ram = Type("RAM", base_level, components)

    ddr3_constructor = Constructor('Some DDR3 RAM', {})
    ddr4_constructor = Constructor('Some DDR4 RAM', {})

    ram.add_constructor(ddr3_constructor.name, ddr3_constructor)
    ram.add_constructor(ddr4_constructor.name, ddr4_constructor)

    gpu = Type("GPU", base_level, components)

    gpu1_constructor = Constructor('Some Nvidia GPU', {})
    gpu2_constructor = Constructor('Some GeForce GPU', {})

    gpu.add_constructor(gpu1_constructor.name, gpu1_constructor)
    gpu.add_constructor(gpu2_constructor.name, gpu2_constructor)

    components.add_type(cpu.name, cpu) 
    components.add_type(ram.name, ram) 
    components.add_type(gpu.name, gpu) 

    # добавляем сведения о совместимости компонентов 
    # совместимость компонентов мы выражаем через сигма-тип
    # совместимость можно генерировать более сложно, на основе 
    # свойств объектов. но здесь мы упростили процесс, задаем своместимость 
    # между компонентами явно
    
    # cpu_ram - Product-тип, комбинация cpu и ram
    cpu_ram = (cpu, ram) 

    # check_compat - предикат, который проверяет совместимость компонентов
    # для упрощения мы предполагаем, что типы всегда совместимы
    # x: элемент типа cpu_ram
    # у: элемент типа gpu 
    # предполагается, что если компоненты совместимы, будет
    # возвращен типа unit, либо проведена попытка создать пустой тип в
    # противном случае
    check_compat = lambda x,y: unit 
    cpu_ram_gpu = (cpu_ram, gpu)

    # совместимость компонентов мы представляем как сигма-тип, где  
    # - в качестве первого элемента - 
    #   тройка (cpu, ram, gpu) == Product(Product(cpu, ram), gpu)
    # - в качестве второго элемента - 
    # свидетельство их совместимости
    make_compatibility_type = lambda cpu_ram, gpu: \
                          Sigma(domain = tuple,\
                          codomain = check_compat,\
                          first = cpu_ram_gpu,\
                          second = unit)

    # сигма-тип совместимости компонентов также 
    # находится в universe 0, поэтому мы добавляем его  
    compatibility_type = Type("Compatibility", base_level, components_level)

    # принимает на вход сигма-тип Compatibility объявленный ранее  
    compatibility_constructor  = Constructor(compatibility_type.name,\
                                             {'constructor': make_compatibility_type})

    compatibility_type.add_constructor(compatibility_constructor.name,\
                                       compatibility_constructor)

    components.add_type(compatibility_type.name, compatibility_type)

    # Шаг 2. Конструируем universe 2. Данный universe содержит
    # единственный тип - конфигурацию компьютера.
    # Невозможность создания конфигурации из несовместимых компонентов 
    # обеспечивается необходимостью указывать в конструкторе конфигурации
    # свидетельства совместимости компонентов (тип Compatibility). 
    # конструктор конфигурации нельзя вызвать если свидетельство совместимсти 
    # отсутствует. 
    config = Type("Configuration", components_level, components)
    config_constructor = Constructor('generic config', 
                                   {'cpu':cpu,
                                    'ram':ram,
                                    'gpu':gpu,
                                    'compatibility':compatibility_type
                                    })
    
    config.add_constructor(config_constructor.name, config_constructor)
    configurations.add_type(config.name, config)

    # Шаг 3. Конструируем universe 3.  
    # В этом universe содержатся типы, которые представляют собой шаблоны
    # шаблон в нашей реализации - это Пи-тип, который сопоставляет каждой
    # конкретной конфигурации результат: 
    # - unit, если конфигурация соответствует шаблону
    # - empty в противном случае
    # за счет того, что шаблон - это совершенно другой тип, 
    # его нельзя использовать при создании конкретной конфигурации, 
    # такой вызов не пройдет проверку типов
    
    # вспомогательная функция для определения соответствия конкретного конфига
    # заданному шаблону; для простоты всегда возвращает unit 
    validate_config_aganist_template = lambda config: unit 

    # Пи-тип, который соответствует заданному шаблону конфигурации
    template_validation = lambda config: \
                          Pi(domain = Type,\
                          codomain = validate_config_aganist_template,\
                          first = config,\
                          second = unit)

    template = Type("TemplateGeneric", configurations_level, templates)
    template_constructor = Constructor('generic template', 
                                      { 
                                       'template_validator': template_validation,
                                       'configuration': config
                                      })
    template.add_constructor(template_constructor.name, template_constructor)
    templates.add_type(template.name, template)


# функция проверки доступа
# по сути это Пи-тип, который получает на вход 
# Product(subject, Document), выдавая тип-свидетельство 
# того, что документ можно читать, в данном случае - сам документ
# либо empty
# для упрощения, оформил этот тип как функцию
def can_read(subject: Type, document: Type) -> Type|Empty:
    # если уровни документа и читателя совпадают, 
    # то чтение разрешено
    if subject.level.value == document.level.value:
        return document

    # чтение взаимодействие на разных уровнях запрещено, 
    # поэтмоу, чтобы субъект с большим уровнем допуска
    # прочитал документ с меньшим уровнем доступа
    # соответствующий документ нужно "поднять" 
    if subject.level.value > document.level.value:
        return UniversePolymorphism.lift(document,\
                                         subject.level.value - document.level.value)

    # если прав доступа нет, то возвращаем пустой тип
    return Empty


def document_system():
    public_level = Level(0)
    public_universe = Universe(public_level)

    internal_level = Level(1)
    internal_universe = Universe(internal_level)

    secret_level = Level(2)
    secret_universe = Universe(secret_level)

    public_doc = Type('public doc', public_level, public_universe)
    anyone = Type('anyone', public_level, public_universe)

    internal_doc = Type('internal doc', internal_level, internal_universe)
    staff = Type('staff', internal_level, internal_universe)

    secret_doc = Type('secret doc', secret_level, secret_universe)
    cleared = Type('cleared ', secret_level, secret_universe)

    assert can_read(anyone, public_doc) == public_doc
    assert can_read(anyone, secret_doc) == Empty
    assert can_read(anyone, internal_doc) == Empty
    assert can_read(cleared, internal_doc).level.value == cleared.level.value




# Пи-тип, оформленный как функция
# для иллюстрации реализовали простейшие проверки на 
# то, что поля непустые. более сложную валидацию опустили
def fullname_consistency(fullname:Type) -> Unit|Empty:
    is_consistent = fullname.first_name is not Empty and\
                    fullname.surname is not Empty and\
                    fullname.middle_name is not Empty
    if is_consistent:
        return unit

    return Empty


# для иллюстрации реализовали простейшие проверки на 
# то, что поля непустые. более сложную валидацию опустили
def phone_num_consistency(phone_num:Type) -> Unit|Empty:
    is_consistent  = phone_num.country_code is not Empty and \
                     phone_num.internal_number is not Empty
    if is_consistent:
        return unit
    return Empty


# функция валидации формы
# позволяет проверять дополнительные отношения 
# между её частями
# в данном случае для краткости всегда возвращает unit
def form_validity(form:Type) -> Unit|Empty:
    return unit


def forms_validator():
    basic_level = Level(0)

    basic_types_level = Level(1)
    basic_types = Universe(basic_types_level)

    composite_types_level = Level(2)
    composite_types = Universe(composite_types_level)

    forms_level = Level(3)
    forms = Universe(forms_level)
    
    # Шаг 1. Определение базовых типов
    string = Type("string", basic_level, basic_types)
    number = Type("number", basic_level, basic_types)

    string_constructor = Constructor('string', {'value':str} )
    number_constructor = Constructor('number', {'value':int} )

    string.add_constructor(string_constructor.name, string_constructor)
    number.add_constructor(number_constructor.name, number_constructor)

    basic_types.add_type(string.name, string)
    basic_types.add_type(number.name, number)


    # Шаг 2. Создание составных типов на примере номера телефона и полного имени
    # конструктор конструктор типов требует свидетельства того, что их поля валидны
    # свидетельство валидности полей представляет собой сигма-тип, где 
    # валидному составному полю соответствует unit, а невалидонму - Empty
    full_name = Type("full_name", basic_types_level, composite_types)

    # сигма-тип для свидетельства валидности полного имени
    fullname_validity_evidence = lambda fullname: \
                          Sigma(domain = Type,\
                          codomain = fullname_consistency,\
                          first = fullname,\
                          second = unit)

    fullname_validity_evidence_type = Type("fullname validity", \
                                   basic_types_level, composite_types)

    fullname_validity_evidence_constructor  = Constructor(fullname_validity_evidence_type.name,\
                                             {'evidence': fullname_validity_evidence})

    fullname_validity_evidence_type.add_constructor(fullname_validity_evidence_constructor.name,\
                                       fullname_validity_evidence_constructor)

    composite_types.add_type(fullname_validity_evidence_type.name, fullname_validity_evidence_type)


    full_name_constructor = Constructor('full_name', \
                                     {'first_name':string,
                                      'surname': string,
                                      'middle_name': string,
                                      'validity_evidence': Sigma} )

    full_name.add_constructor(full_name_constructor.name, full_name_constructor)
    composite_types.add_type(full_name.name, full_name)


    # сигма-тип для свидетельства валидности номера телефона
    phone_num_validity_evidence = lambda phone: \
                          Sigma(domain = Type,\
                          codomain = phone_num_consistency,\
                          first = phone,\
                          second = unit)

    phone_num_validity_type = Type("phone_num validity", \
                                   basic_types_level, composite_types)

    phone_num_validity_constructor  = Constructor(phone_num_validity_type.name,\
                                             {'evidence': phone_num_validity_evidence})

    phone_num_validity_type.add_constructor(phone_num_validity_constructor.name,\
                                       phone_num_validity_constructor)

    composite_types.add_type(phone_num_validity_type.name, phone_num_validity_type)


    phone_num_constructor = Constructor('phone_num', \
                                        {'country_code':number,
                                         'internal_number': number,
                                         'validity_evidence': Sigma} )

    phone_num = Type("phone_num", basic_types_level, composite_types)

    phone_num.add_constructor(phone_num_constructor.name, phone_num_constructor)
    composite_types.add_type(phone_num.name, phone_num)


    # Шаг 3. Конструирование форм
    # Здесь появляется возможность переиспользования составных полей 
    # из предыдущего уровня для формирования новых форм, через 
    # их комбинацию Sum и Product-типами
    # конструктор типа принимает также свидетельство валидности 
    # составных форм + может добавлять новые. 
    # Таким образом система типов не даст нам создать невалидную форму
    # На этом уровне можно добавлять дополнительную логику валидации 

    
    # сигма-тип для свидетельства валидности формы
    form_validity_evidence = lambda form: \
                          Sigma(domain = Type,\
                          codomain = form_validity,\
                          first = form,\
                          second = unit)

    form_validity_type = Type("form validity", \
                              composite_types_level, forms)

    form_validity_constructor  = Constructor(form_validity_type.name,\
                                             {'evidence': form_validity_evidence})

    form_validity_type.add_constructor(form_validity_constructor.name,\
                                       form_validity_constructor)

    forms.add_type(form_validity_type.name, form_validity_type)


    form_constructor = Constructor('form constructor', \
                                    {'phone':phone_num,
                                      'full_name': full_name,
                                      'validity_evidence': Sigma} )

    form = Type("form", composite_types_level, forms)
    
    form.add_constructor(form_constructor.name, form_constructor)
    forms.add_type(form.name, form)


if __name__ == "__main__":
    configure_pc()
    document_system()
    forms_validator()
