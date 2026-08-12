"""Static bank of TEF Canada Section B ("point de vue") writing prompts.

Replaces on-demand AI question generation (formerly prompt_question_generation.py).
Each entry's statement is sourced from published TEF Canada Section B practice
material (see source_url); the numbered Type de document / Objectif / Consignes
framing mirrors the exam's own standard Section B task instructions, including
the official guidance that a letter format is not required.
"""

_TEMPLATE = """1. Type de document: une phrase extraite d'un journal ou d'un article
2. Objectif: exposer et défendre votre point de vue (200 mots minimum)
3. Consignes:
   - Minimum 200 mots.
   - Développez vos arguments en plusieurs paragraphes (au moins 2-3).
   - Utilisez un style formel et respectueux.
   - Vous n'êtes pas obligé(e) de rédiger votre réponse sous forme de lettre.
4. Situation de départ: {statement}"""

# (title, statement, source_url)
_RAW = [
    ("Internet et isolement social",
     "« L'utilisation d'Internet et les réseaux sociaux nous rendent isolés de la société. »",
     "https://lingorelic.com/tef-canada-expression-ecrite-section-b-lutilisation-dinternet-nous-rend-isoles-de-la-societe/"),
    ("Addiction aux réseaux sociaux chez les adultes",
     "« Addiction aux réseaux sociaux, les adultes aussi sont fortement touchés. »",
     "https://lingorelic.com/tef-canada-expression-ecrite-section-b-addiction-aux-reseaux-sociaux-les-adultes-aussi-sont-fortement-touches/"),
    ("Avions à usage unique",
     "« Les avions devraient être utilisés une seule fois. »",
     "https://lingorelic.com/2024/04/tef-canada-expression-ecrite-section-b-les-avions-devraient-etre/"),
    ("Sport et corruption",
     "« Le sport est plein de corruption. »",
     "https://lingorelic.com/tef-canada-writing-section-b-le-sport-et-la-corruption/"),
    ("Publicité et comportement d'achat",
     "« La publicité influence le comportement de nos achats. »",
     "https://lingorelic.com/tef-canada-writing-section-b-linfluence-de-la-publicite/"),
    ("Smartphones pour les personnes âgées",
     "« Il faut équiper toutes les personnes âgées de smartphones. »",
     "https://lingorelic.com/tef-canada-writing-section-b-les-personnes-agees-et-les-smartphones/"),
    ("Gratuité des transports en commun",
     "« Il faut rendre les transports en commun gratuits. »",
     "https://lingorelic.com/tef-canada-writing-section-b-rendre-les-transports-publics-gratuits/"),
    ("La place de la femme n'a pas évolué",
     "« La place de la femme n'a pas évolué depuis 100 ans. »",
     "https://lingorelic.com/2023/06/tef-canada-expression-ecrite-section-b-writing-sample-task/"),
    ("Apprendre uniquement l'anglais",
     "« Il est inutile d'apprendre une autre langue que l'anglais. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Instrument de musique obligatoire",
     "« Les enfants devraient être obligés d'apprendre à jouer un instrument de musique. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Culture gratuite pour tous",
     "« La culture devrait être complètement gratuite afin d'être accessible au plus grand nombre. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Argent de poche aux adolescents",
     "« Donner de l'argent de poche aux adolescents est un mauvais service que nous leur rendons. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Discipline : le rôle des professeurs",
     "« Les professeurs sont ceux qui doivent apprendre la discipline à leurs élèves. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Droit de vote dès 16 ans",
     "« Les jeunes de plus de seize ans devraient avoir le droit de vote. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Robots et chômage",
     "« Les robots et la technologie vont tous nous mettre au chômage. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Danger des nouvelles technologies",
     "« Il faut s'opposer au développement de nouvelles technologies dangereuses pour l'Homme. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Télétravail obligatoire",
     "« Le travail à distance devrait toujours être obligatoire lorsqu'il est possible. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Sites de rencontre et éloignement",
     "« Les sites de rencontres nous éloignent plus qu'ils ne nous rapprochent. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Internet transforme les citoyens en consommateurs",
     "« Internet et les réseaux sociaux ont transformé les citoyens en simples consommateurs. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Réseaux sociaux, danger pour les jeunes",
     "« Les réseaux sociaux représentent un grave danger pour les jeunes. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Salaires excessifs des sportifs",
     "« Les sportifs professionnels gagnent trop d'argent. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Nourriture à base d'insectes",
     "« Nous devrons bientôt manger de la nourriture à base d'insectes pour subvenir aux besoins des huit milliards d'êtres humains sur Terre. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Voyages organisés et découverte réelle",
     "« Les voyages organisés sont incompatibles avec la découverte réelle d'un pays. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Tourisme et développement mondial",
     "« Les touristes contribuent au développement du monde de façon très significative. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Pollution des avions",
     "« Les avions sont polluants et leur utilisation devrait être plus régulée qu'à l'heure actuelle. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Animaux de compagnie et liberté",
     "« Avoir des animaux de compagnie est cruel. Les animaux sont faits pour vivre en liberté. »",
     "https://frademy.com/liste-sujets-tef"),
    ("Repasser le permis après 70 ans",
     "« Les personnes âgées de plus de 70 ans devraient obligatoirement repasser leur permis de conduire. »",
     "https://frademy.com/liste-sujets-tef"),
]

QUESTIONS_TASK_B = [
    {
        "id": f"b{idx + 1:02d}",
        "title": title,
        "preview": statement,
        "prompt": _TEMPLATE.format(statement=statement),
        "source_url": source_url,
    }
    for idx, (title, statement, source_url) in enumerate(_RAW)
]
