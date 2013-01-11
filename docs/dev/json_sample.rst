===============================
Data Model (samples) JSON / XML
===============================

JSON Sample with xpath
======================

.. code-block:: javascript

    {
        'front': {
            'journal-title': '/front/journal-meta/journal-title-group/journal-title',
            'abbrev-journal-title': '/front/journal-meta/journal-title-group/abbrev-journal-title',
            'issn': '/articles/article/front/journal-meta/issn',
            'publisher-name': '/articles/article/front/journal-meta/publisher/publisher-name',
            'publisher-loc': '/articles/article/front/journal-meta/publisher/publisher-loc',
            'journal-id': '/front/journal-meta/journal-id',
            'default-language': '/articles/article/@xml:lang',
            'pub-date': {
                'month': '/articles/article/front/article-meta/pub-date/month',
                'year': '/articles/article/front/article-meta/pub-date/year',
                'day': '/articles/article/front/article-meta/pub-date/day'
            },
            'volume': '/articles/article/front/article-meta/volume',
            'number': '/articles/article/front/article-meta/issue',
            'fpage': '/articles/article/front/article-meta/fpage',
            'lpage': '/articles/article/front/article-meta/lpage',
            'article-ids': {
                'publisher-id': '/articles/article/front/article-meta/article-id[@pub-id-type="publisher-id"]',
                'doi': '/articles/article/front/article-meta/article-id[@pub-id-type="doi"]'
            },
            'subjects': {
                'wos': [
                    '/articles/article/front/article-meta/article-categories/subj-group[0]',
                    '/articles/article/front/article-meta/article-categories/subj-group[0]'
                ],
                'cnpq': ['public health']
            },
            'title-group': {
                '/articles/article/front/article-meta/title-group/article-title/@xml:lang': '/articles/article/front/article-meta/title-group/article-title',
                '/articles/article/front/article-meta/title-group/trans-title-group/@xml:lang': '/articles/article/front/article-meta/title-group/trans-title-group',
            },
            'contrib-group': {
                '/articles/article/front/article-meta/contrib-group/contrib/@contrib-type': [
                    {
                    'surname': '/articles/article/front/article-meta/contrib-group/contrib/name/surname',
                    'given-names': '/articles/article/front/article-meta/contrib-group/contrib/name/given-names',
                    'role': '/articles/article/front/article-meta/contrib-group/contrib/role',
                    'affiliations': '/articles/article/front/article-meta/contrib-group/contrib/xref'
                    },
                ],
                'affiliations': [
                    {
                    'addr-line': '/articles/article/front/article-meta/aff/addr-line',
                    'institution': '/articles/article/front/article-meta/aff/institution',
                    'country': '/articles/article/front/article-meta/aff/country',
                    'ref': '/articles/article/front/article-meta/aff/@id',
                    },
                ],
                'abstract': {
                    '/articles/article/front/article-meta/abstract/@xml:lang': '/articles/article/front/article-meta/abstract',
                    '/articles/article/front/article-meta/trans-abstract@xml:lang': '/articles/article/front/article-meta/trans-abstract',
                },
                'keyword-group': {
                    '/articles/article/front/article-meta/kwd-group/@xml"lang': [
                        '/articles/article/front/article-meta/kwd-group/kwd[0]', 
                        '/articles/article/front/article-meta/kwd-group/kwd[1]',
                        '/articles/article/front/article-meta/kwd-group/kwd[2]'
                    ],
                    '/articles/article/front/article-meta/kwd-group/@xml"lang': [
                        '/articles/article/front/article-meta/kwd-group/kwd[0]', 
                        '/articles/article/front/article-meta/kwd-group/kwd[1]',
                        '/articles/article/front/article-meta/kwd-group/kwd[2]'
                    ]
                }
            },

        },
        'body': u'<p>All body content</p>',
        'back': [
            {
                'article-title': u'Alternatives for logistic regression in cross-sectional studies: an empirical comparison of models that directly estimate the prevalence ratio',
                'type': u'journal'
            }
        ]
    }

JSON Sample with data
=====================

.. code-block:: javascript

    {
        'front': {
            'journal-title': u'Revista de Saúde Pública',
            'abbrev-journal-title': u'Rev. Saúde Pública',
            'issn': '0034-8910',
            'publisher-name': u'Faculdade de Saúde pública da Universidade de São Paulo',
            'publisher-loc': u'São Paulo',
            'journal-id': u'rsp',
            'default-language': u'pt',
            'pub-date': {
                'month': u'08',
                'year': u'2010'
            },
            'volume': u'44',
            'number': u'4',
            'fpage': u'601',
            'lpage': u'610',
            'urls': {
                'full-text-page': u'http://www.scielo.br/scielo.php?script=sci_arttext&amp;pid=S0034-89102010000400003&amp;lng=en&amp;tlng=en',
                'issue-page': u'http://www.scielo.br/scielo.php?script=sci_issuetoc&amp;pid=S0034-891020100004&amp;lng=en&amp;tlng=en',
                'journal-page': u'http://www.scielo.br/scielo.php?script=sci_serial&amp;pid=0034-8910&amp;lng=en&amp;tlng=en'
            },
            'article-ids': {
                'publisher-id': u'S0034-89102010000400003',
                'doi': u'10.1590/S0034-89102010000400003'
            },
            'subjects': {
                'wos': [u'PUBLIC, ENVIROMENTAL & OCCUPATIONAL HEATH', u'SOCIOLOGY'],
                'cnpq': [u'public health']
            },
            'title-group': {
                'pt': u'Uso de medicamentos por pessoas com deficiências em áreas do estado de São Paulo',
                'es': u'Uso de medicamentos por personas con deficiencias en áreas del Estado de Sao Paulo, Sureste de Brasil',
                'en': u'Use of medicines by persons with disabilities in São Paulo state areas, Southeastern Brazil'
            },
            'contrib-group': {
                'authors': [{
                    'surname': u'Castro',
                    'given-names': u'Shamyr Sulyvan',
                    'role': u'ND',
                    'affiliations': [u'A01']
                    },
                    {
                    'surname': u'Pelicione',
                    'given-names': u'Americo Focesi',
                    'role': u'ND',
                    'affiliations': [u'A02']
                    },
                    {
                    'surname': u'Cesar',
                    'given-names': u'Chester Luiz Galvão',
                    'role': u'ND',
                    'affiliations': [u'A03']
                    },
                    {
                    'surname': u'Carandina',
                    'given-names': u'Luana',
                    'role': u'ND',
                    'affiliations': [u'A04']
                    },
                    {
                    'surname': u'Barros',
                    'given-names': u'Marilisa Berti de Azevedo',
                    'role': u'ND',
                    'affiliations': [u'A05']
                    },
                    {
                    'surname': u'Alves',
                    'given-names': u'Maria Cecilia Goi Porto',
                    'role': u'ND',
                    'affiliations': [u'A06']
                    },
                    {
                    'surname': u'Goldbaum',
                    'given-names': u'Moisés',
                    'role': u'ND',
                    'affiliations': [u'A07']
                    },
                ],
                'coordinators': [
                    {
                    'surname': u'Goldbaum',
                    'given-names': u'Moisés',
                    'role': u'ND',
                    'affiliations': [u'A07']
                    },
                ],
                'affiliations': [
                    {
                    'addr-line': u'São Paulo',
                    'institution': u'Universidade de São Paulo',
                    'country': u'Brasil',
                    'ref': u'A01',
                    },
                    {
                    'addr-line': u'São Paulo',
                    'institution': u'Faculdades Metropolitanas Unidas',
                    'country': u'Brasil',
                    'ref': u'A02',
                    },
                    {
                    'addr-line': u'São Paulo',
                    'institution': u'USP',
                    'country': u'Brasil',
                    'ref': u'A03',
                    },
                    {
                    'addr-line': u'Botucatu',
                    'institution': u'Universidade Estadual Paulista Julio de Mesquita Filho',
                    'country': u'Brasil',
                    'ref': u'A04',
                    },
                    {
                    'addr-line': u'Campinas',
                    'institution': u'Universidade Federal de Campinas',
                    'country': u'Brasil',
                    'ref': u'A05',
                    },
                    {
                    'addr-line': u'São Paulo',
                    'institution': u'Secretaria de Saúde do Estado de São Paulo',
                    'country': u'Brasil',
                    'ref': u'A06',
                    },
                    {
                    'addr-line': u'São Paulo',
                    'institution': u'USP',
                    'country': u'Brasil',
                    'ref': u'A07',
                    },
                ],
                'abstract': {
                    'pt': u'OBJETIVO: Analisar o consumo de medicamentos e os principais grupos terapêuticos consumidos por pessoas com deficiências físicas, auditivas ou visuais. MÉTODOS: Estudo transversal em que foram analisados dados do Inquérito Multicêntrico de Saúde no Estado de São Paulo (ISA-SP) em 2002 e do Inquérito de Saúde no Município de São Paulo (ISA-Capital), realizado em 2003. Os entrevistados que referiram deficiências foram estudados segundo as variáveis que compõem o banco de dados: área, sexo, renda, faixa etária, raça, consumo de medicamentos e tipos de medicamentos consumidos. RESULTADOS: A percentagem de consumo entre as pessoas com deficiência foi de: 62,8% entre os visuais; 60,2% entre os auditivos e 70,1% entre os físicos. As pessoas com deficiência física consumiram 20% mais medicamentos que os não-deficientes. Entre as pessoas com deficiência visual, os medicamentos mais consumidos foram os diuréticos, agentes do sistema renina-angiotensina e analgésicos. Pessoas com deficiência auditiva utilizaram mais analgésicos e agentes do sistema renina-angiotensina. Entre indivíduos com deficiência física, analgésicos, antitrombóticos e agentes do sistema renina-angiotensina foram os medicamentos mais consumidos. CONCLUSÕES: Houve maior consumo de medicamentos entre as pessoas com deficiências quando comparados com os não-deficientes, sendo os indivíduos com deficiência física os que mais consumiram fármacos, seguidos de deficientes visuais e auditivos.',
                    'es': u'OBJETIVO: Analizar el consumo de medicamentos y los principales grupos terapéuticos consumidos por personas con deficiencias físicas, auditivas o visuales. MÉTODOS: Estudio transversal en que fueron analizados datos de la Pesquisa Multicentrica de Salud en el Estado de Sao Paulo (ISA-SP) en 2002 y de la Pesquisa de Salud en el Municipio de Sao Paulo (ISA-Capital), realizado en 2003. Los entrevistados que refirieron deficiencias fueron estudiados según las variables que componen el banco de datos: área, sexo, renta, grupo etario, raza, consumo de medicamentos y tipos de medicamentos consumidos. RESULTADOS: El porcentaje de consumo entre las personas con deficiencia fue de: 62,8% entre los visuales; 60,2% entre los auditivos y de 70,1% entre los físicos. Las personas con deficiencia física consumieron 20% más medicamentos que los no deficientes. Entre las personas con deficiencia visual, los medicamentos más consumidos fueron los diuréticos, agentes del sistema renina-angiotensina y analgésicos. Personas con deficiencia auditiva utilizaron más analgésicos y agentes del sistema renina-angiotensina. Entre individuos con deficiencia física, analgésicos, antitrombóticos y agentes del sistema renina-angiotensina fueron los medicamentos más consumidos. CONCLUSIONES: Hubo mayor consumo de medicamentos entre las personas con deficiencias al compararse con los no deficientes, siendo los individuos con deficiencia física los que más consumieron fármacos, seguidos de los deficientes visuales y auditivos.',
                    'en': u'OBJECTIVE: To analyze the use of medicines and the main therapeutic groups consumed by persons with physical, hearing and visual disabilities. METHODS: A cross-sectional study was performed, where data from the 2002 Inquérito Multicêntrico de Saúde no Estado de São Paulo (ISA-SP - São Paulo State Multicenter Health Survey), as well as the 2003 Inquérito de Saúde no Município de São Paulo (ISA-Capital - City of São Paulo Health Survey), Southeastern Brazil, were analyzed. Respondents who reported having disabilities were studied, according to variables that comprise the database: geographic area, gender, income, age group, ethnic group, use of medicines and types of drugs consumed. RESULTS: The percentage of use of drugs by persons with disabilities was 62.8% among the visually impaired; 60.2% among the hearing impaired; and 70.1% among the persons with physical disabilities. Individuals with physical disabilities consumed 20% more medications than non-disabled ones. Among persons with visual disabilities, the most frequently consumed drugs were diuretics, agents of the renin-angiotensin system and analgesics. Persons with hearing disabilities used more analgesics and agents of the renin-angiotensin system. Among those with physical disabilities, analgesics, antithrombotics and agents of the renin-angiotensin system were the most frequently consumed medicines. CONCLUSIONS: There was a greater use of medicines among persons with disabilities than non-disabled ones. Persons with physical disabilities were those who most consumed medicines, followed by the visually impaired and the hearing impaired.'
                },
                'keyword-group': {
                    'pt': [u'Pessoas com Deficiência', u'Uso de Medicamentos', u'Inquéritos de Morbidade'],
                    'es': [u'Personas con Discapacidad', u'Utilización de Medicamentos', u'Medicamentos de Uso Contínuo', u'Encuestas de Morbilidad'],
                    'en': [u'Disabled Persons', u'Drug Utilization', u'Drugs of Continuous Use', u'Morbidity Surveys']
                }
            },

        },
        'body': u'<p>All body content</p>',
        'back': [
            {
                'article-title': u'Alternatives for logistic regression in cross-sectional studies: an empirical comparison of models that directly estimate the prevalence ratio',
                'type': u'journal'
            }
        ]
    }

XML Sample
==========

.. code-block:: xml

    <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" dtd-version="3.0" article-type="research-article" lang_id="pt">
        <front>
            <journal-meta>
                <journal-id journal-id-type="publisher">rsp</journal-id>
                <journal-title-group>
                    <journal-title>Revista de Saúde Pública</journal-title>
                    <abbrev-journal-title>Rev. Saúde Pública</abbrev-journal-title>
                </journal-title-group>
                <issn>0034-8910</issn>
                <publisher>
                    <publisher-name>Faculdade de Saúde Pública da Universidade de São Paulo</publisher-name>
                    <publisher-loc>São Paulo</publisher-loc>
                </publisher>
            </journal-meta>
            <article-meta>
                <unique-article-id pub-id-type="publisher-id">S0034-89102010000400003</unique-article-id>
                <article-id pub-id-type="publisher-id">S0034-89102010000400003</article-id>
                <article-id pub-id-type="doi">10.1590/S0034-89102010000400003</article-id>
                <article-categories>
                    <subj-group>
                        <subject>PUBLIC, ENVIRONMENTAL &amp; OCCUPATIONAL HEALTH</subject>
                        <subject>SOCIOLOGY</subject>
                    </subj-group>
                </article-categories>
                <title-group>
                    <article-title lang_id="pt">Uso de medicamentos por pessoas com deficiências em áreas do estado de São Paulo</article-title>
                    <trans-title-group lang_id="en">
                        <trans-title>Use of medicines by persons with disabilities in São Paulo state areas, Southeastern Brazil</trans-title>
                    </trans-title-group>
                    <trans-title-group lang_id="es">
                        <trans-title>Uso de medicamentos por personas con deficiencias en áreas del Estado de Sao Paulo, Sureste de Brasil</trans-title>
                    </trans-title-group>
                </title-group>
                <contrib-group>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Castro</surname>
                            <given-names>Shamyr Sulyvan</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A01"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Pelicioni</surname>
                            <given-names>Americo Focesi</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A02"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Cesar</surname>
                            <given-names>Chester Luiz Galvão</given-names>
                        </name><role>ND</role>
                        <xref ref-type="aff" rid="A03"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Carandina</surname>
                            <given-names>Luana</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A04"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Barros</surname>
                            <given-names>Marilisa Berti de Azevedo</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A05"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Alves</surname>
                            <given-names>Maria Cecilia Goi Porto</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A06"></xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name>
                            <surname>Goldbaum</surname>
                            <given-names>Moisés</given-names>
                        </name>
                        <role>ND</role>
                        <xref ref-type="aff" rid="A07"></xref>
                    </contrib>
                </contrib-group>
                <aff id="A01">
                    <addr-line>São Paulo</addr-line>
                    <institution>Universidade de São Paulo</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A02">
                    <addr-line>São Paulo</addr-line>
                    <institution>Faculdades Metropolitanas Unidas</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A03">
                    <addr-line>São Paulo</addr-line>
                    <institution>USP</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A04">
                    <addr-line>Botucatu</addr-line>
                    <institution>Universidade Estadual Paulista Julio de Mesquita Filho</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A05">
                    <addr-line>Campinas</addr-line>
                    <institution>Universidade Estadual de Campinas</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A06">
                    <addr-line>São Paulo</addr-line>
                    <institution>Secretaria de Saúde do Estado de São Paulo</institution>
                    <country>Brasil</country>
                </aff>
                <aff id="A07">
                    <addr-line>São Paulo</addr-line>
                    <institution>USP</institution>
                    <country>Brasil</country>
                </aff>
                <pub-date>
                    <month>08</month>
                    <year>2010</year>
                </pub-date>
                <volume>44</volume>
                <issue>4</issue>
                <fpage>601</fpage>
                <lpage>610</lpage>
                <abstract lang_id="pt">
                    <p>OBJETIVO: Analisar o consumo de medicamentos e os principais grupos terapêuticos consumidos por pessoas com deficiências físicas, auditivas ou visuais. MÉTODOS: Estudo transversal em que foram analisados dados do Inquérito Multicêntrico de Saúde no Estado de São Paulo (ISA-SP) em 2002 e do Inquérito de Saúde no Município de São Paulo (ISA-Capital), realizado em 2003. Os entrevistados que referiram deficiências foram estudados segundo as variáveis que compõem o banco de dados: área, sexo, renda, faixa etária, raça, consumo de medicamentos e tipos de medicamentos consumidos. RESULTADOS: A percentagem de consumo entre as pessoas com deficiência foi de: 62,8% entre os visuais; 60,2% entre os auditivos e 70,1% entre os físicos. As pessoas com deficiência física consumiram 20% mais medicamentos que os não-deficientes. Entre as pessoas com deficiência visual, os medicamentos mais consumidos foram os diuréticos, agentes do sistema renina-angiotensina e analgésicos. Pessoas com deficiência auditiva utilizaram mais analgésicos e agentes do sistema renina-angiotensina. Entre indivíduos com deficiência física, analgésicos, antitrombóticos e agentes do sistema renina-angiotensina foram os medicamentos mais consumidos. CONCLUSÕES: Houve maior consumo de medicamentos entre as pessoas com deficiências quando comparados com os não-deficientes, sendo os indivíduos com deficiência física os que mais consumiram fármacos, seguidos de deficientes visuais e auditivos.</p>
                </abstract>
                <trans-abstract lang_id="en">
                    <p>OBJECTIVE: To analyze the use of medicines and the main therapeutic groups consumed by persons with physical, hearing and visual disabilities. METHODS: A cross-sectional study was performed, where data from the 2002 Inquérito Multicêntrico de Saúde no Estado de São Paulo (ISA-SP - São Paulo State Multicenter Health Survey), as well as the 2003 Inquérito de Saúde no Município de São Paulo (ISA-Capital - City of São Paulo Health Survey), Southeastern Brazil, were analyzed. Respondents who reported having disabilities were studied, according to variables that comprise the database: geographic area, gender, income, age group, ethnic group, use of medicines and types of drugs consumed. RESULTS: The percentage of use of drugs by persons with disabilities was 62.8% among the visually impaired; 60.2% among the hearing impaired; and 70.1% among the persons with physical disabilities. Individuals with physical disabilities consumed 20% more medications than non-disabled ones. Among persons with visual disabilities, the most frequently consumed drugs were diuretics, agents of the renin-angiotensin system and analgesics. Persons with hearing disabilities used more analgesics and agents of the renin-angiotensin system. Among those with physical disabilities, analgesics, antithrombotics and agents of the renin-angiotensin system were the most frequently consumed medicines. CONCLUSIONS: There was a greater use of medicines among persons with disabilities than non-disabled ones. Persons with physical disabilities were those who most consumed medicines, followed by the visually impaired and the hearing impaired.</p>
                </trans-abstract>
                <trans-abstract lang_id="es">
                    <p>OBJETIVO: Analizar el consumo de medicamentos y los principales grupos terapéuticos consumidos por personas con deficiencias físicas, auditivas o visuales. MÉTODOS: Estudio transversal en que fueron analizados datos de la Pesquisa Multicentrica de Salud en el Estado de Sao Paulo (ISA-SP) en 2002 y de la Pesquisa de Salud en el Municipio de Sao Paulo (ISA-Capital), realizado en 2003. Los entrevistados que refirieron deficiencias fueron estudiados según las variables que componen el banco de datos: área, sexo, renta, grupo etario, raza, consumo de medicamentos y tipos de medicamentos consumidos. RESULTADOS: El porcentaje de consumo entre las personas con deficiencia fue de: 62,8% entre los visuales; 60,2% entre los auditivos y de 70,1% entre los físicos. Las personas con deficiencia física consumieron 20% más medicamentos que los no deficientes. Entre las personas con deficiencia visual, los medicamentos más consumidos fueron los diuréticos, agentes del sistema renina-angiotensina y analgésicos. Personas con deficiencia auditiva utilizaron más analgésicos y agentes del sistema renina-angiotensina. Entre individuos con deficiencia física, analgésicos, antitrombóticos y agentes del sistema renina-angiotensina fueron los medicamentos más consumidos. CONCLUSIONES: Hubo mayor consumo de medicamentos entre las personas con deficiencias al compararse con los no deficientes, siendo los individuos con deficiencia física los que más consumieron fármacos, seguidos de los deficientes visuales y auditivos</p>
                </trans-abstract>
                <kwd-group lang_id="en" kwd-group-type="author-generated">
                    <kwd>Disabled Persons</kwd>
                    <kwd>Drug Utilization</kwd>
                    <kwd>Drugs of Continuous Use</kwd>
                    <kwd>Morbidity Surveys</kwd>
                </kwd-group>
                <kwd-group lang_id="es" kwd-group-type="author-generated">
                    <kwd>Personas con Discapacidad</kwd>
                    <kwd>Utilización de Medicamentos</kwd>
                    <kwd>Medicamentos de Uso Contínuo</kwd>
                    <kwd>Encuestas de Morbilidad</kwd>
                </kwd-group>
                <kwd-group lang_id="pt" kwd-group-type="author-generated">
                    <kwd>Pessoas com Deficiência</kwd>
                    <kwd>Uso de Medicamentos</kwd>
                    <kwd>Inquéritos de Morbidade</kwd>
                </kwd-group>
            </article-meta>
        </front>
        <back>
            <ref-list>
                <ref id="B1">
                    <element-citation publication-type="article">
                        <article-title>Alternatives for logistic regression in cross-sectional studies: an empirical comparison of models that directly estimate the prevalence ratio</article-title>
                        <source>BMC Med Res Methodol</source>
                        <date>
                            <year>2003</year>
                        </date>
                        <fpage>21</fpage>
                        <volume>3</volume>
                        <person-group>
                            <name>
                                <surname>Barros</surname>
                                <given-names>AJD</given-names>
                            </name>
                        </person-group>
                    </element-citation>
                </ref>
            </ref-list>
        </back>
    </article>