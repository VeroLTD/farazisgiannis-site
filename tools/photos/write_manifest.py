#!/usr/bin/env python3
"""Writes tools/photos/manifest.json — the single list of every photograph on farazisgiannis.com (14 Oct 2026 audit).

Owner's rules (14 Oct 2026): every photo matches its topic, and NO photo appears twice anywhere on the site (also not
in a different crop, not as a hero, a card or a social-preview image). So every slot below is used on exactly one page,
and none of them is one of the photographs inside the short films (assets/video/SOURCES.md) or the explainer posters;
tools/photos/audit.py checks that with image fingerprints, check.py checks that the built pages use each slot once.

Licences: CC0 1.0 / Public Domain only for the photos in the repository (the AVRASTRO library, vero-os
apps/website/content/photos/credits.json). Slots with "fetch" are downloaded on GitHub's machines by the workflow
«Site photos» (.github/workflows/photos.yml → tools/photos/fetch.py): Pixabay Content License (only with the secret
PIXABAY_API_KEY) or CC0 / Public Domain from Openverse. Edit the data here, then: python3 tools/photos/write_manifest.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CC0 = {'license': 'CC0 1.0', 'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/'}

def credit(title, creator, page, ov_id):
    return {'title': title, 'creator': creator, 'page': page, 'openverse_id': ov_id, **CC0}

def alt(el, en, ru): return {'el': el, 'en': en, 'ru': ru}

SLOTS = {
    # ---- home page: the nine subjects (one photo each; the Solutions page shows the narrated films instead)
    'sol-life': {'page': 'home', 'use': 'card: Life insurance', 'src': 'sol-life.webp',
                 'alt': alt('Πατέρας κρατά απαλά το χεράκι του μωρού του', 'A father gently holding his baby’s hand', 'Отец бережно держит ручку своего малыша'),
                 'credit': credit("Free father holding baby's hand", None, 'https://www.rawpixel.com/image/5904571/photo-image-public-domain-hands-kid', '855aa0e8-805e-4d3e-9ab4-0a4471491955')},
    'sol-health': {'page': 'home', 'use': 'card: Health and medical cover', 'src': 'sol-health.webp',
                   'alt': alt('Γιατροί σε διάδρομο νοσοκομείου', 'Doctors in a hospital corridor', 'Врачи в коридоре больницы'),
                   'credit': credit('Doctors Hospital', 'Oles kanebckuu', 'https://stocksnap.io/photo/doctors-hospital-5YUFL6LC0E', '373a2ccd-73e0-4e8c-bd07-b0d611b7ac6e')},
    'sol-accident': {'page': 'home', 'use': 'card: Personal accident', 'src': 'sol-accident.webp',
                     'alt': alt('Χαμογελαστό παιδί παίζει έξω με μια μπάλα', 'A smiling child playing outdoors with a ball', 'Улыбающийся ребёнок играет с мячом на улице'),
                     'credit': credit('Happy Kid', 'Lukáš Rychvalský', 'https://stocksnap.io/photo/happy-kid-X2XRVZYTZ1', 'ff76a7e5-2460-4ffd-9d4d-7c98b77970f5'),
                     # a closer match for «injury and the income you lose»; replaces the photo above once downloaded
                     'fetch': {'replace': True, 'queries': ['physiotherapy knee injury', 'physiotherapist patient rehabilitation', 'man arm sling injury'],
                               'alt': alt('Φυσικοθεραπεία μετά από τραυματισμό', 'Physiotherapy after an injury', 'Физиотерапия после травмы')}},
    'sol-retirement': {'page': 'home', 'use': 'card: Retirement', 'src': 'sol-retirement.webp',
                       'alt': alt('Ζευγάρι μεγαλύτερης ηλικίας χαμογελά μπροστά σε ένα tablet', 'An older couple smiling over a tablet at home', 'Пожилая пара с улыбкой смотрит на планшет дома'),
                       'credit': credit('Happy Couple', 'Senior Living', 'https://stocksnap.io/photo/happy-couple-L54KROOB9E', 'ce8fe730-75ea-4484-a000-b462df2f8f6f')},
    'sol-savings': {'page': 'home', 'use': 'card: Savings', 'src': 'sol-savings.webp',
                    'alt': alt('Ροζ κουμπαράς με κέρματα', 'A pink piggy bank with coins', 'Розовая копилка с монетами'),
                    'credit': credit('Free coins image', None, 'https://www.rawpixel.com/image/5906370/photo-image-public-domain-money-free', '1c7124d3-d250-44bb-82ab-3a582d8f3e79')},
    'sol-education': {'page': 'home', 'use': 'card: Children and education', 'src': 'sol-education.webp',
                      'alt': alt('Παιδί ζωγραφίζει με μολύβια σε ένα τετράδιο', 'A child drawing with pencils in a notebook', 'Ребёнок рисует карандашами в блокноте'),
                      'credit': credit('Free child drawing pencil notepad', None, 'https://www.rawpixel.com/image/5926180/photo-image-public-domain-kid-person', '66c6c193-b950-491b-9201-4a1dfea08cea')},
    'sol-loan': {'page': 'home', 'use': 'card: Loan protection', 'src': 'sol-loan.webp',
                 'alt': alt('Κλειδί στην κλειδαριά της εξώπορτας ενός σπιτιού', 'A key in the lock of a front door', 'Ключ в замке входной двери'),
                 'credit': credit('Keys Door', 'WDnet Studio', 'https://stocksnap.io/photo/keys-door-Z1TKDI29FZ', 'deb7b5c9-590d-41e2-9b6c-7c7196d45f7d')},
    'sol-business': {'page': 'home', 'use': 'card: Business protection', 'src': 'sol-business.webp',
                     'alt': alt('Αρτοποιός βγάζει φρέσκο ψωμί από τον φούρνο', 'A baker taking fresh bread out of the oven', 'Пекарь достаёт из печи свежий хлеб'),
                     'credit': credit('Free fresh artisan bread oven', None, 'https://www.rawpixel.com/image/5904163/photo-image-public-domain-person-food', '581ff4cc-97c6-405f-a791-564d32f6f7d5')},
    'sol-review': {'page': 'home', 'use': 'card: Policy reviews', 'src': 'sol-review.webp',
                   'alt': alt('Χέρι υπογράφει έγγραφα σε έναν φάκελο', 'A hand signing documents in a binder', 'Рука подписывает документы в папке'),
                   'credit': credit('Signing contract', None, 'https://www.rawpixel.com/image/5917619/signing-contract-free-public-domain-cc0-photo', 'f91e65b5-bca7-49c5-9f2c-0541565a4be4')},
    # ---- How I work: the four steps and «Before we talk»
    'how-talk': {'page': 'how', 'use': 'step 1: a first conversation', 'src': 'how-talk.webp',
                 'alt': alt('Γυναίκα με το κινητό και έναν καφέ μπροστά στον υπολογιστή της', 'A woman with her phone and a cup of coffee at her laptop', 'Женщина с телефоном и чашкой кофе за ноутбуком'),
                 'credit': credit('Girl Woman', 'Wilfred Iven', 'https://stocksnap.io/photo/girl-woman-70JMTNDBJI', '55d9dbde-12f6-4497-a73e-1deb306b6f09')},
    'how-needs': {'page': 'how', 'use': 'step 2: looking at your needs', 'src': 'how-needs.webp',
                  'alt': alt('Χέρι σημειώνει αριθμούς δίπλα σε μια αριθμομηχανή', 'A hand noting figures beside a calculator', 'Рука записывает цифры рядом с калькулятором'),
                  'credit': credit('Accountant. Free public domain CC0', None, 'https://www.rawpixel.com/image/5913662/accountant-free-public-domain-cc0-photo', '9fc07d00-e550-4448-bfc5-98438a83dfd2')},
    'how-proposal': {'page': 'how', 'use': 'step 3: a proposal in plain words', 'src': 'how-proposal.webp',
                     'alt': alt('Μια γραπτή πρόταση σε πινακίδα με κλιπ, πάνω σε γραφείο', 'A written proposal on a clipboard on a desk', 'Письменное предложение на планшете с зажимом на столе'),
                     'credit': credit('Office Work', 'Châu Thông Phan', 'https://stocksnap.io/photo/office-work-UP9J4EZYNJ', 'b3be6880-561e-4926-bc94-de401f44d115')},
    'how-after': {'page': 'how', 'use': 'step 4: with you afterwards', 'src': 'how-after.webp',
                  'alt': alt('Χειραψία', 'A handshake', 'Рукопожатие'),
                  'credit': credit('Work Business', 'Matt Moloney', 'https://stocksnap.io/photo/work-business-WQ2JMRIIQB', '934f04e8-0913-4155-8e31-b0869d08e266')},
    'how-prepare': {'page': 'how', 'use': 'Before we talk', 'src': 'how-prepare.webp',
                    'alt': alt('Υπολογιστής με ένα υπολογιστικό φύλλο και μια αριθμομηχανή', 'A laptop with a spreadsheet, and a calculator', 'Ноутбук с таблицей и калькулятор'),
                    'credit': credit('Accounting Finance', 'Wilfred Iven', 'https://stocksnap.io/photo/accounting-finance-JONMP7TPGK', '9b7ef946-1e8c-4654-bd90-ee183d6056a3')},
    # ---- Guides: one per guide
    'guide-life': {'page': 'guides', 'use': 'guide: how much life cover', 'src': 'guide-life.webp',
                   'alt': alt('Πατέρας αγκαλιάζει τον χαμογελαστό γιο του', 'A father hugging his smiling son', 'Отец обнимает улыбающегося сына'),
                   'credit': credit('Father Son', 'Family Moments', 'https://stocksnap.io/photo/father-son-HBKFP7NCLL', 'bfbc01c8-4783-4354-a83a-62e8e47ce31d')},
    'guide-gesy': {'page': 'guides', 'use': 'guide: GESY and a private plan', 'src': 'guide-gesy.webp',
                   'alt': alt('Γιατρός συζητά με μια ασθενή', 'A doctor talking with a patient', 'Врач беседует с пациенткой'),
                   'credit': credit('Doctor Patient', 'Direct Media', 'https://stocksnap.io/photo/doctor-patient-2CKENQVERF', '009250f6-639d-4100-aa1b-c536809e8869')},
    'guide-review': {'page': 'guides', 'use': 'guide: when to review', 'src': 'guide-review.webp',
                     'alt': alt('Χέρι γράφει σε ένα ημερολόγιο', 'A hand writing in a planner', 'Рука делает запись в ежедневнике'),
                     'credit': credit('Writing Hand', 'Kristin Hardwick', 'https://stocksnap.io/photo/writing-hand-2FRRD2PUVA', '0fd12f2a-5497-4577-ba8f-e8b0a5d32407')},
    # ---- page headers of the newer pages
    'first-meeting': {'page': 'first', 'use': 'page header', 'src': 'first-meeting.webp',
                      'alt': alt('Τρία άτομα συζητούν μπροστά σε έναν υπολογιστή', 'Three people talking over a laptop', 'Трое людей беседуют у ноутбука'),
                      'credit': credit('Business People', 'Direct Media', 'https://stocksnap.io/photo/business-people-DUXISHKTT3', 'e2b49788-c79b-4d17-be4f-7b3307803f9b')},
    'staff-talks': {'page': 'employers', 'use': 'page header', 'src': 'staff-talks.webp',
                    'alt': alt('Γυναίκα με tablet σε γραφείο, με συναδέλφους πίσω της', 'A woman with a tablet in an office, colleagues behind her', 'Женщина с планшетом в офисе, за ней коллеги'),
                    'credit': credit('Business Woman', 'Direct Media', 'https://stocksnap.io/photo/business-woman-S81ZPXJZUU', '47630adb-c428-49bb-ac22-3be84632bd21')},
    # ---- city pages: one photo of each place, downloaded by the workflow (none in the library). Until then the city
    # page header has no photo. The free Famagusta district only (Ayia Napa, Protaras, Paralimni, Cape Greco).
    'city-nicosia': {'page': 'city-nicosia', 'use': 'page header', 'fetch': {'queries': ['Nicosia Cyprus', 'Lefkosia', 'Nicosia old town', 'Nicosia Venetian walls']},
                     'alt': alt('Άποψη της Λευκωσίας', 'A view of Nicosia', 'Вид Никосии')},
    'city-limassol': {'page': 'city-limassol', 'use': 'page header', 'fetch': {'queries': ['Limassol Cyprus', 'Limassol marina', 'Limassol seafront', 'Limassol old port']},
                      'alt': alt('Άποψη της Λεμεσού', 'A view of Limassol', 'Вид Лимасола')},
    'city-larnaca': {'page': 'city-larnaca', 'use': 'page header', 'fetch': {'queries': ['Larnaca Cyprus', 'Larnaca Finikoudes', 'Larnaca seafront', 'Saint Lazarus church Larnaca']},
                     'alt': alt('Άποψη της Λάρνακας', 'A view of Larnaca', 'Вид Ларнаки')},
    'city-paphos': {'page': 'city-paphos', 'use': 'page header', 'fetch': {'queries': ['Paphos harbour', 'Paphos Cyprus', 'Paphos castle', 'Pafos']},
                    'alt': alt('Άποψη της Πάφου', 'A view of Paphos', 'Вид Пафоса')},
    'city-famagusta': {'page': 'city-famagusta', 'use': 'page header', 'fetch': {'queries': ['Ayia Napa Cyprus', 'Protaras Cyprus', 'Cape Greco Cyprus', 'Paralimni Cyprus']},
                       'alt': alt('Άποψη της ελεύθερης επαρχίας Αμμοχώστου', 'A view of the free Famagusta district', 'Вид свободной части района Фамагусты')},
}

def main():
    path = os.path.join(HERE, 'manifest.json')
    old = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    out = {
        'note': 'Every photograph on farazisgiannis.com, one slot = one place on one page (the same page in el/en/ru). '
                'Made by tools/photos/write_manifest.py; variants by tools/photos/make_variants.py; checked by tools/photos/audit.py.',
        'widths': [480, 960, 1440],
        'reserved': old.get('reserved', {}),   # fingerprints of the film photos and explainer posters (audit.py --reserve)
        'slots': SLOTS,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('manifest:', len(SLOTS), 'slots')

if __name__ == '__main__':
    main()
