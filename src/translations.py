# Ko'p tillilik: barcha foydalanuvchiga ko'rinadigan matnlar shu yerda.
# Tillar: ru (asl/standart), uz, tr, en, kk.
# Har bir kalit uchun barcha 5 til mavjud bo'lishi kerak - i18n.t() shunga tayanadi.

SUPPORTED_LANGUAGES = ('ru', 'uz', 'tr', 'en', 'kk')

LANGUAGE_NAMES = {
    'ru': 'Русский', 'uz': 'Oʻzbekcha', 'tr': 'Türkçe', 'en': 'English', 'kk': 'Қазақша',
}

T = {
    # ---------- Rollar ----------
    'role_don': {
        'ru': 'дон мафии', 'uz': 'mafiya boshligʻi', 'tr': 'mafya babası',
        'en': 'mafia don', 'kk': 'мафия боссы',
    },
    'role_mafia': {
        'ru': 'мафия', 'uz': 'mafiya', 'tr': 'mafya', 'en': 'mafia', 'kk': 'мафия',
    },
    'role_sheriff': {
        'ru': 'шериф', 'uz': 'sherif', 'tr': 'şerif', 'en': 'sheriff', 'kk': 'шериф',
    },
    'role_peace': {
        'ru': 'мирный житель', 'uz': 'tinch aholi', 'tr': 'sivil',
        'en': 'civilian', 'kk': 'тыныш тұрғын',
    },

    # ---------- lang.py shablonlari ----------
    'game_created': {
        'ru': 'Игра создана.\nСоздатель игры: {owner}.\nВремя удаления игры: {time} UTC.\n{order}',
        'uz': 'Oʻyin yaratildi.\nOʻyin egasi: {owner}.\nOʻyin oʻchirilish vaqti: {time} UTC.\n{order}',
        'tr': 'Oyun oluşturuldu.\nOyunu oluşturan: {owner}.\nOyunun silinme zamanı: {time} UTC.\n{order}',
        'en': 'Game created.\nGame owner: {owner}.\nGame deletion time: {time} UTC.\n{order}',
        'kk': 'Ойын құрылды.\nОйын иесі: {owner}.\nОйынды жою уақыты: {time} UTC.\n{order}',
    },
    'cards_taken': {
        'ru': 'Игра начата!\n\nПорядок игроков следующий:\n{order}\n\nИгроки с номерами [{not_took}], разбираем карты!',
        'uz': 'Oʻyin boshlandi!\n\nOʻyinchilar tartibi quyidagicha:\n{order}\n\n[{not_took}] raqamli oʻyinchilar, kartalarni oling!',
        'tr': 'Oyun başladı!\n\nOyuncu sırası şu şekilde:\n{order}\n\n[{not_took}] numaralı oyuncular, kartaları alın!',
        'en': 'Game started!\n\nPlayer order is as follows:\n{order}\n\nPlayers numbered [{not_took}], take your cards!',
        'kk': 'Ойын басталды!\n\nОйыншылар кезегі мынадай:\n{order}\n\n[{not_took}] нөмірлі ойыншылар, карталарды алыңдар!',
    },
    'morning_message': {
        'ru': '{peaceful_night}Идёт день {day}.\nУ вас есть время, чтобы решить, за кого вы проголосуете сегодняшним вечером.\n──────────────────\nИгроки:\n{order}',
        'uz': '{peaceful_night}{day}-kun boshlandi.\nBugun kechqurun kimga ovoz berishni hal qilish uchun vaqtingiz bor.\n──────────────────\nOʻyinchilar:\n{order}',
        'tr': '{peaceful_night}{day}. gün başladı.\nBu akşam kime oy vereceğinize karar vermek için zamanınız var.\n──────────────────\nOyuncular:\n{order}',
        'en': '{peaceful_night}Day {day} has begun.\nYou have time to decide who to vote for this evening.\n──────────────────\nPlayers:\n{order}',
        'kk': '{peaceful_night}{day}-күн басталды.\nБүгін кешке кімге дауыс беретініңізді шешуге уақытыңыз бар.\n──────────────────\nОйыншылар:\n{order}',
    },
    'peaceful_night': {
        'ru': 'Доброе утро, город!\nЭтой ночью обошлось без смертей.\n',
        'uz': 'Xayrli tong, shahar!\nBu kecha hech kim oʻlmadi.\n',
        'tr': 'Günaydın şehir!\nBu gece kimse ölmedi.\n',
        'en': 'Good morning, town!\nNo one died tonight.\n',
        'kk': 'Қайырлы таң, қала!\nБүгін түнде ешкім өлмеді.\n',
    },
    'vote_time': {
        'ru': 'Город, настало время для голосования!\n{vote}',
        'uz': 'Shahar, ovoz berish vaqti keldi!\n{vote}',
        'tr': 'Şehir, oylama zamanı geldi!\n{vote}',
        'en': 'Town, it is time to vote!\n{vote}',
        'kk': 'Қала, дауыс беру уақыты келді!\n{vote}',
    },
    'gallows_word_label': {
        'ru': 'Слово', 'uz': 'Soʻz', 'tr': 'Kelime', 'en': 'Word', 'kk': 'Сөз',
    },
    'gallows_attempts_label': {
        'ru': 'Попытки', 'uz': 'Urinishlar', 'tr': 'Denemeler', 'en': 'Attempts', 'kk': 'Әрекеттер',
    },

    # ---------- game.py ----------
    'team_won': {
        'ru': 'Победили игроки команды "{role}"!',
        'uz': '"{role}" jamoasi gʻalaba qozondi!',
        'tr': '"{role}" takımı kazandı!',
        'en': 'Team "{role}" has won!',
        'kk': '"{role}" командасы жеңді!',
    },
    'game_over_roles_reveal': {
        'ru': 'Игра окончена! {reason}\n\nРоли были распределены следующим образом:\n{roles}',
        'uz': 'Oʻyin tugadi! {reason}\n\nRollar quyidagicha taqsimlangan edi:\n{roles}',
        'tr': 'Oyun bitti! {reason}\n\nRoller şu şekilde dağıtılmıştı:\n{roles}',
        'en': 'Game over! {reason}\n\nRoles were distributed as follows:\n{roles}',
        'kk': 'Ойын аяқталды! {reason}\n\nРөлдер былай бөлінген еді:\n{roles}',
    },

    # ---------- stages.py ----------
    'game_over_no_cards': {
        'ru': 'Игра окончена! Игроки не взяли свои карты.',
        'uz': "Oʻyin tugadi! Oʻyinchilar oʻz kartalarini olishmadi.",
        'tr': 'Oyun bitti! Oyuncular kartlarını almadı.',
        'en': 'Game over! Players did not take their cards.',
        'kk': 'Ойын аяқталды! Ойыншылар өз карталарын алмады.',
    },
    'meet_team_button': {
        'ru': 'Познакомиться с командой', 'uz': 'Jamoa bilan tanishish',
        'tr': 'Takımla tanış', 'en': 'Meet the team', 'kk': 'Командамен танысу',
    },
    'finish_selection_button': {
        'ru': 'Закончить выбор', 'uz': 'Tanlashni tugatish',
        'tr': 'Seçimi bitir', 'en': 'Finish selection', 'kk': 'Таңдауды аяқтау',
    },
    'don_choose_order_instruction': {
        'ru': '{don}, тебе предстоит сделать свой выбор и определить порядок выстрелов твоей команды.\nДля этого последовательно нажимай на номера игроков, а после этого нажми на кнопку "{finish_selection}".',
        'uz': '{don}, tanlov qilish va jamoangizning otish tartibini belgilash navbati sizda.\nBuning uchun oʻyinchilar raqamlarini ketma-ket bosing, soʻng "{finish_selection}" tugmasini bosing.',
        'tr': '{don}, seçimini yapıp takımının ateş sırasını belirleme sırası sende.\nBunun için oyuncuların numaralarına sırayla bas, ardından "{finish_selection}" düğmesine bas.',
        'en': '{don}, it is your turn to make a choice and determine your team\'s shooting order.\nTo do this, press the players\' numbers one by one, then press the "{finish_selection}" button.',
        'kk': '{don}, таңдау жасап, командаңыздың ату кезегін белгілеу кезегі сізде.\nОл үшін ойыншылардың нөмірлерін кезекпен басыңыз, содан кейін "{finish_selection}" түймесін басыңыз.',
    },
    'get_order_button': {
        'ru': '✉ Получить приказ', 'uz': '✉ Buyruqni olish',
        'tr': '✉ Emri al', 'en': '✉ Get orders', 'kk': '✉ Бұйрықты алу',
    },
    'don_order_given_to_mafia': {
        'ru': '{don} записал приказ. {mafia}, получите конверт со своим заданием!',
        'uz': '{don} buyruqni yozib qoʻydi. {mafia}, topshirig\'ingiz bilan konvertni oling!',
        'tr': '{don} emri yazdı. {mafia}, görev zarfınızı alın!',
        'en': '{don} has recorded the order. {mafia}, get the envelope with your assignment!',
        'kk': '{don} бұйрықты жазып қойды. {mafia}, тапсырмаңыз бар хатты алыңыздар!',
    },
    'dont_vote_option': {
        'ru': 'Не голосовать', 'uz': 'Ovoz bermaslik',
        'tr': 'Oy verme', 'en': "Don't vote", 'kk': 'Дауыс бермеу',
    },
    'town_voted_criminal_jailed': {
        'ru': 'Народным голосованием в тюрьму был посажен игрок {number} ({name}).',
        'uz': 'Xalq ovozi bilan {number}-oʻyinchi ({name}) qamoqqa tiqildi.',
        'tr': 'Halk oylamasıyla {number} numaralı oyuncu ({name}) hapse atıldı.',
        'en': 'By popular vote, player {number} ({name}) was sent to jail.',
        'kk': 'Халық дауыс беруі бойынша {number}-ойыншы ({name}) түрмеге жабылды.',
    },
    'town_no_criminal_chosen': {
        'ru': 'Город не выбрал преступника.',
        'uz': 'Shahar jinoyatchini tanlamadi.',
        'tr': 'Şehir bir suçlu seçmedi.',
        'en': 'The town did not choose a criminal.',
        'kk': 'Қала қылмыскерді таңдамады.',
    },
    'criminal_saved_by_documents': {
        'ru': 'Народным голосованием было решено посадить в тюрьму игрока {number} ({name}), но у него оказались поддельные документы - он остался в городе!',
        'uz': "Xalq ovozi bilan {number}-oʻyinchi ({name}) qamoqqa tiqilishi kerak edi, lekin uning soxta hujjatlari bor ekan - u shaharda qoldi!",
        'tr': '{number} numaralı oyuncu ({name}) halk oylamasıyla hapse atılacaktı, ama sahte belgeleri çıktı - şehirde kaldı!',
        'en': 'Player {number} ({name}) was voted to be jailed, but they had fake documents - they stayed in town!',
        'kk': '{number}-ойыншы ({name}) халық дауысымен түрмеге жабылуы керек еді, бірақ оның жалған құжаттары бар екен - қалада қалды!',
    },
    'victim_saved_by_protection': {
        'ru': 'Доброе утро, город!\nЭтой ночью мафия пыталась убить игрока {number} ({name}), но он был под защитой и остался жив!',
        'uz': "Xayrli tong, shahar!\nBu kecha mafiya {number}-oʻyinchini ({name}) oʻldirmoqchi boʻldi, lekin u himoya ostida edi va tirik qoldi!",
        'tr': 'Günaydın şehir!\nBu gece mafya {number} numaralı oyuncuyu ({name}) öldürmeye çalıştı, ama o korumadaydı ve hayatta kaldı!',
        'en': 'Good morning, town!\nTonight the mafia tried to kill player {number} ({name}), but they were protected and survived!',
        'kk': 'Қайырлы таң, қала!\nБүгін түнде мафия {number}-ойыншыны ({name}) өлтірмек болды, бірақ ол қорғауда болды және тірі қалды!',
    },
    'night_falls_mafia_wakes': {
        'ru': 'Наступает ночь. Город засыпает. {mafia}, приготовьтесь к выстрелу...',
        'uz': 'Tun boshlandi. Shahar uyquga ketdi. {mafia}, otishga tayyorlaning...',
        'tr': 'Gece çöküyor. Şehir uykuya dalıyor. {mafia}, ateşe hazırlanın...',
        'en': 'Night falls. The town goes to sleep. {mafia}, prepare to shoot...',
        'kk': 'Түн түсті. Қала ұйықтап жатыр. {mafia}, атуға дайындалыңыздар...',
    },
    'mafia_choosing_victim': {
        'ru': '{mafia} выбирает жертву.\n',
        'uz': '{mafia} qurbon tanlamoqda.\n',
        'tr': '{mafia} kurban seçiyor.\n',
        'en': '{mafia} is choosing a victim.\n',
        'kk': '{mafia} құрбан таңдап жатыр.\n',
    },
    'mafia_sleeps_don_checks': {
        'ru': '{mafia} засыпает. {don} совершает свою проверку.\n',
        'uz': '{mafia} uxlaydi. {don} tekshiruvini oʻtkazadi.\n',
        'tr': '{mafia} uyuyor. {don} kontrolünü yapıyor.\n',
        'en': '{mafia} goes to sleep. {don} performs their check.\n',
        'kk': '{mafia} ұйықтайды. {don} тексеруін жүргізеді.\n',
    },
    'don_sleeps_sheriff_checks': {
        'ru': '{don} засыпает. Просыпается {sheriff} и совершает свою проверку.\n',
        'uz': '{don} uxlaydi. {sheriff} uygʻonib, tekshiruvini oʻtkazadi.\n',
        'tr': '{don} uyuyor. {sheriff} uyanıp kontrolünü yapıyor.\n',
        'en': '{don} goes to sleep. {sheriff} wakes up and performs their check.\n',
        'kk': '{don} ұйықтайды. {sheriff} оянып, тексеруін жүргізеді.\n',
    },
    'morning_victim_killed': {
        'ru': 'Доброе утро, город!\nПечальные новости: этой ночью был убит игрок {number} ({name}).',
        'uz': 'Xayrli tong, shahar!\nAchinarli xabar: bu kecha {number}-oʻyinchi ({name}) oʻldirildi.',
        'tr': 'Günaydın şehir!\nÜzücü haber: bu gece {number} numaralı oyuncu ({name}) öldürüldü.',
        'en': 'Good morning, town!\nSad news: player {number} ({name}) was killed tonight.',
        'kk': 'Қайырлы таң, қала!\nҚайғылы жаңалық: бүгін түнде {number}-ойыншы ({name}) өлтірілді.',
    },

    # ---------- handlers.py: start/help ----------
    'start_message': {
        'ru': 'Привет, я {name}!\nЯ умею создавать игры в мафию в группах и супергруппах.\nИнструкция и исходный код: https://gitlab.com/r4rdsn/mafia_host_bot\nПо всем вопросам пишите на https://t.me/r4rdsn',
        'uz': 'Salom, men {name}man!\nMen guruh va supergruppalarda mafiya oʻyinlarini yarataman.\nQoʻllanma va manba kodi: https://gitlab.com/r4rdsn/mafia_host_bot\nSavollar boʻlsa: https://t.me/r4rdsn',
        'tr': 'Merhaba, ben {name}!\nGrup ve süper gruplarda mafya oyunları oluşturabilirim.\nKılavuz ve kaynak kod: https://gitlab.com/r4rdsn/mafia_host_bot\nSorularınız için: https://t.me/r4rdsn',
        'en': "Hi, I'm {name}!\nI can create mafia games in groups and supergroups.\nInstructions and source code: https://gitlab.com/r4rdsn/mafia_host_bot\nFor any questions, message https://t.me/r4rdsn",
        'kk': 'Сәлем, мен {name}мын!\nМен топтар мен супертоптарда мафия ойындарын жасай аламын.\nНұсқаулық және бастапқы код: https://gitlab.com/r4rdsn/mafia_host_bot\nСұрақтар үшін: https://t.me/r4rdsn',
    },

    # ---------- handlers.py: statistika/reyting ----------
    'stats_empty': {
        'ru': 'Статистика {name} пуста.', 'uz': '{name} statistikasi boʻsh.',
        'tr': '{name} istatistiği boş.', 'en': "{name}'s statistics are empty.",
        'kk': '{name} статистикасы бос.',
    },
    'mafia_score_line': {
        'ru': 'Счёт {name} в мафии: {score}',
        'uz': '{name} ning mafiyadagi hisobi: {score}',
        'tr': "{name}'in mafyadaki skoru: {score}",
        'en': "{name}'s mafia score: {score}",
        'kk': '{name} мафиядағы есебі: {score}',
    },
    'wins_ratio_line': {
        'ru': 'Побед: {win}/{total} ({percent}%)',
        'uz': 'Gʻalabalar: {win}/{total} ({percent}%)',
        'tr': 'Galibiyet: {win}/{total} (%{percent})',
        'en': 'Wins: {win}/{total} ({percent}%)',
        'kk': 'Жеңістер: {win}/{total} ({percent}%)',
    },
    'role_wins_line': {
        'ru': 'побед - {win}/{total} ({rate}%)',
        'uz': 'gʻalabalar - {win}/{total} ({rate}%)',
        'tr': 'galibiyet - {win}/{total} (%{rate})',
        'en': 'wins - {win}/{total} ({rate}%)',
        'kk': 'жеңістер - {win}/{total} ({rate}%)',
    },
    'croco_score_line': {
        'ru': 'Счёт {name} в крокодиле: {score}',
        'uz': '{name} ning krokodildagi hisobi: {score}',
        'tr': "{name}'in kroko oyunundaki skoru: {score}",
        'en': "{name}'s crocodile score: {score}",
        'kk': '{name} крокодилдегі есебі: {score}',
    },
    'guessed_words_line': {
        'ru': 'Угадано: {guesses}', 'uz': 'Topildi: {guesses}',
        'tr': 'Bilinen: {guesses}', 'en': 'Guessed: {guesses}', 'kk': 'Тапты: {guesses}',
    },
    'gallows_letters_line': {
        'ru': 'Угадано букв в виселице: {right}/{total} ({percent}%)',
        'uz': 'Osilgan odamda topilgan harflar: {right}/{total} ({percent}%)',
        'tr': 'Adam asmacada bilinen harf: {right}/{total} (%{percent})',
        'en': 'Letters guessed in hangman: {right}/{total} ({percent}%)',
        'kk': 'Дарға асуда тапқан әріптер: {right}/{total} ({percent}%)',
    },
    'chat_stats_empty': {
        'ru': 'Статистика чата пуста.', 'uz': 'Chat statistikasi boʻsh.',
        'tr': 'Sohbet istatistiği boş.', 'en': 'Chat statistics are empty.',
        'kk': 'Чат статистикасы бос.',
    },
    'mafia_rating_title': {
        'ru': 'Рейтинг игроков в мафию:\n', 'uz': 'Mafiya oʻyinchilari reytingi:\n',
        'tr': 'Mafya oyuncuları sıralaması:\n', 'en': 'Mafia player ranking:\n',
        'kk': 'Мафия ойыншылары рейтингі:\n',
    },
    'croco_rating_title': {
        'ru': 'Рейтинг игроков в крокодила:\n', 'uz': 'Krokodil oʻyinchilari reytingi:\n',
        'tr': 'Kroko oyuncuları sıralaması:\n', 'en': 'Crocodile player ranking:\n',
        'kk': 'Крокодил ойыншылары рейтингі:\n',
    },

    # ---------- handlers.py: o'yin yaratish / qo'shilish ----------
    'game_already_running': {
        'ru': 'Игра в этом чате уже идёт.', 'uz': 'Bu chatda oʻyin allaqachon ketmoqda.',
        'tr': 'Bu sohbette zaten bir oyun devam ediyor.', 'en': 'A game is already running in this chat.',
        'kk': 'Бұл чатта ойын әлдеқашан жүріп жатыр.',
    },
    'get_word_button': {
        'ru': 'Получить слово', 'uz': 'Soʻzni olish', 'tr': 'Kelimeyi al',
        'en': 'Get the word', 'kk': 'Сөзді алу',
    },
    'croco_game_started': {
        'ru': 'Игра началась! {name}, у тебя есть две минуты, чтобы объяснить слово.',
        'uz': 'Oʻyin boshlandi! {name}, soʻzni tushuntirish uchun ikki daqiqa vaqting bor.',
        'tr': 'Oyun başladı! {name}, kelimeyi anlatmak için iki dakikan var.',
        'en': 'The game has started! {name}, you have two minutes to explain the word.',
        'kk': 'Ойын басталды! {name}, сөзді түсіндіруге екі минут уақытың бар.',
    },
    'your_word_is': {
        'ru': 'Твоё слово: {word}.', 'uz': 'Soʻzingiz: {word}.',
        'tr': 'Kelimen: {word}.', 'en': 'Your word: {word}.', 'kk': 'Сіздің сөзіңіз: {word}.',
    },
    'cant_get_word': {
        'ru': 'Ты не можешь получить слово для этой игры.',
        'uz': 'Siz bu oʻyin uchun soʻz ololmaysiz.',
        'tr': 'Bu oyun için kelime alamazsın.',
        'en': 'You cannot get a word for this game.',
        'kk': 'Сіз бұл ойын үшін сөз ала алмайсыз.',
    },
    'take_card_button': {
        'ru': '🃏 Вытянуть карту', 'uz': '🃏 Karta olish',
        'tr': '🃏 Kart çek', 'en': '🃏 Draw a card', 'kk': '🃏 Карта тарту',
    },
    'your_role_is': {
        'ru': 'Твоя роль - {role}.', 'uz': 'Sizning rolingiz - {role}.',
        'tr': 'Rolün - {role}.', 'en': 'Your role is - {role}.', 'kk': 'Сіздің рөліңіз - {role}.',
    },
    'player_order_title': {
        'ru': 'Порядок игроков для игры следующий:\n\n',
        'uz': 'Oʻyin uchun oʻyinchilar tartibi quyidagicha:\n\n',
        'tr': 'Oyun için oyuncu sırası şu şekilde:\n\n',
        'en': 'The player order for the game is as follows:\n\n',
        'kk': 'Ойын үшін ойыншылар кезегі мынадай:\n\n',
    },
    'already_have_role': {
        'ru': 'У тебя уже есть роль.', 'uz': 'Sizda allaqachon rol bor.',
        'tr': 'Zaten bir rolün var.', 'en': 'You already have a role.', 'kk': 'Сізде рөл бар болып қойды.',
    },
    'not_playing_here': {
        'ru': 'Ты сейчас не играешь в игру в этой конфе.',
        'uz': 'Siz hozir bu chatdagi oʻyinda ishtirok etmayapsiz.',
        'tr': 'Şu anda bu sohbetteki oyunda oynamıyorsun.',
        'en': 'You are not currently playing a game in this chat.',
        'kk': 'Сіз қазір бұл чаттағы ойында ойнап отырған жоқсыз.',
    },
    'your_team_is': {
        'ru': 'Ты играешь в следующей команде:\n', 'uz': 'Siz quyidagi jamoada oʻynayapsiz:\n',
        'tr': 'Şu takımda oynuyorsun:\n', 'en': 'You are playing on the following team:\n',
        'kk': 'Сіз мына командада ойнап жатырсыз:\n',
    },
    'cant_meet_mafia_team': {
        'ru': 'Ты не можешь знакомиться с командой мафии.',
        'uz': 'Siz mafiya jamoasi bilan tanisha olmaysiz.',
        'tr': 'Mafya takımıyla tanışamazsın.',
        'en': 'You cannot meet the mafia team.',
        'kk': 'Сіз мафия командасымен таныса алмайсыз.',
    },
    'sheriff_check_yes': {
        'ru': 'Да, игрок под номером {number} - {role}',
        'uz': 'Ha, {number}-raqamli oʻyinchi - {role}',
        'tr': 'Evet, {number} numaralı oyuncu - {role}',
        'en': 'Yes, player number {number} is - {role}',
        'kk': 'Иә, {number}-нөмірлі ойыншы - {role}',
    },
    'sheriff_check_no': {
        'ru': 'Нет, игрок под номером {number} - не {role}',
        'uz': "Yo'q, {number}-raqamli oʻyinchi - {role} emas",
        'tr': 'Hayır, {number} numaralı oyuncu - {role} değil',
        'en': 'No, player number {number} is not - {role}',
        'kk': 'Жоқ, {number}-нөмірлі ойыншы - {role} емес',
    },
    'cant_check_as_don': {
        'ru': 'Ты не можешь совершать проверку дона.',
        'uz': 'Siz don tekshiruvini oʻtkaza olmaysiz.',
        'tr': 'Don kontrolünü yapamazsın.',
        'en': 'You cannot perform the don check.',
        'kk': 'Сіз дон тексеруін жүргізе алмайсыз.',
    },
    'don_check_is_don': {
        'ru': 'Да, игрок под номером {number} - {role}',
        'uz': 'Ha, {number}-raqamli oʻyinchi - {role}',
        'tr': 'Evet, {number} numaralı oyuncu - {role}',
        'en': 'Yes, player number {number} is - {role}',
        'kk': 'Иә, {number}-нөмірлі ойыншы - {role}',
    },
    'don_check_is_mafia': {
        'ru': 'Да, игрок под номером {number} - {role}',
        'uz': 'Ha, {number}-raqamli oʻyinchi - {role}',
        'tr': 'Evet, {number} numaralı oyuncu - {role}',
        'en': 'Yes, player number {number} is - {role}',
        'kk': 'Иә, {number}-нөмірлі ойыншы - {role}',
    },
    'don_check_no': {
        'ru': 'Нет, игрок под номером {number} - не {role}',
        'uz': "Yo'q, {number}-raqamli oʻyinchi - {role} emas",
        'tr': 'Hayır, {number} numaralı oyuncu - {role} değil',
        'en': 'No, player number {number} is not - {role}',
        'kk': 'Жоқ, {number}-нөмірлі ойыншы - {role} емес',
    },
    'cant_check_as_sheriff': {
        'ru': 'Ты не можешь совершать проверку шерифа.',
        'uz': 'Siz sherif tekshiruvini oʻtkaza olmaysiz.',
        'tr': 'Şerif kontrolünü yapamazsın.',
        'en': 'You cannot perform the sheriff check.',
        'kk': 'Сіз шериф тексеруін жүргізе алмайсыз.',
    },
    'player_added_to_order': {
        'ru': 'Игрок под номером {number} добавлен в приказ.',
        'uz': '{number}-raqamli oʻyinchi buyruqqa qoʻshildi.',
        'tr': '{number} numaralı oyuncu emre eklendi.',
        'en': 'Player number {number} has been added to the order.',
        'kk': '{number}-нөмірлі ойыншы бұйрыққа қосылды.',
    },
    'cant_give_don_order': {
        'ru': 'Ты не можешь отдавать приказ дона.',
        'uz': 'Siz don buyrugʻini bera olmaysiz.',
        'tr': 'Don emri veremezsin.',
        'en': 'You cannot give the don order.',
        'kk': 'Сіз дон бұйрығын бере алмайсыз.',
    },
    'vote_cast_against': {
        'ru': 'Голос отдан против игрока {number}.',
        'uz': '{number}-oʻyinchiga qarshi ovoz berildi.',
        'tr': '{number} numaralı oyuncuya karşı oy verildi.',
        'en': 'Vote cast against player {number}.',
        'kk': '{number}-ойыншыға қарсы дауыс берілді.',
    },
    'vote_cast': {
        'ru': 'Голос отдан.', 'uz': 'Ovoz berildi.', 'tr': 'Oy verildi.',
        'en': 'Vote cast.', 'kk': 'Дауыс берілді.',
    },
    'vote_cast_double': {
        'ru': 'Голос отдан против игрока {number} (учтён как 2 голоса!).',
        'uz': '{number}-oʻyinchiga qarshi ovoz berildi (2 ovoz sifatida hisoblandi!).',
        'tr': '{number} numaralı oyuncuya karşı oy verildi (2 oy olarak sayıldı!).',
        'en': 'Vote cast against player {number} (counted as 2 votes!).',
        'kk': '{number}-ойыншыға қарсы дауыс берілді (2 дауыс болып есептелді!).',
    },
    'cant_vote': {
        'ru': 'Ты не можешь голосовать.', 'uz': 'Siz ovoz bera olmaysiz.',
        'tr': 'Oy veremezsin.', 'en': 'You cannot vote.', 'kk': 'Сіз дауыс бере алмайсыз.',
    },
    'don_order_recorded_will_pass': {
        'ru': 'Приказ записан и будет передан команде мафии.',
        'uz': 'Buyruq yozib olindi va mafiya jamoasiga yetkaziladi.',
        'tr': 'Emir kaydedildi ve mafya takımına iletilecek.',
        'en': 'The order has been recorded and will be passed to the mafia team.',
        'kk': 'Бұйрық жазылды және мафия командасына жеткізіледі.',
    },
    'don_order_text_with_list': {
        'ru': 'Я отдал тебе следующий приказ: {order}. Стреляем именно в таком порядке, в противном случае промахнёмся. ~ {don}',
        'uz': 'Men senga quyidagi buyruqni berdim: {order}. Aynan shu tartibda otamiz, aks holda oʻq bekor ketadi. ~ {don}',
        'tr': 'Sana şu emri verdim: {order}. Tam bu sırayla ateş ediyoruz, aksi halde ıskalarız. ~ {don}',
        'en': 'I have given you the following order: {order}. We shoot in exactly this order, otherwise we will miss. ~ {don}',
        'kk': 'Мен саған мынадай бұйрық бердім: {order}. Дәл осы ретпен атамыз, әйтпесе өткізіп аламыз. ~ {don}',
    },
    'don_order_text_no_list': {
        'ru': 'Я не отдал приказа, импровизируем по ходу игры. Главное - стрелять в одних и тех же людей в одну ночь, в противном случае промахнёмся. ~ {don}',
        'uz': 'Men buyruq bermadim, oʻyin davomida oʻzimiz hal qilamiz. Asosiysi - bir kechada bir xil odamlarga otish, aks holda oʻq bekor ketadi. ~ {don}',
        'tr': 'Emir vermedim, oyun sırasında doğaçlama yapıyoruz. Önemli olan aynı gece aynı kişilere ateş etmek, aksi halde ıskalarız. ~ {don}',
        'en': 'I have not given an order, we improvise as the game goes. The main thing is to shoot the same people in one night, otherwise we will miss. ~ {don}',
        'kk': 'Мен бұйрық бермедім, ойын барысында өзіміз шешеміз. Ең бастысы - бір түнде бір адамдарға ату, әйтпесе өткізіп аламыз. ~ {don}',
    },
    'cant_receive_don_order': {
        'ru': 'Ты не можешь получать приказ дона.',
        'uz': 'Siz don buyrugʻini ola olmaysiz.',
        'tr': 'Don emrini alamazsın.',
        'en': 'You cannot receive the don order.',
        'kk': 'Сіз дон бұйрығын ала алмайсыз.',
    },
    'left_the_game': {
        'ru': 'Ты больше не в игре.', 'uz': 'Siz endi oʻyinda emassiz.',
        'tr': 'Artık oyunda değilsin.', 'en': 'You are no longer in the game.',
        'kk': 'Сіз енді ойында емессіз.',
    },
    'max_players_reached': {
        'ru': 'В игре состоит максимальное количество игроков.',
        'uz': 'Oʻyinda maksimal sondagi oʻyinchi bor.',
        'tr': 'Oyunda maksimum sayıda oyuncu var.',
        'en': 'The game already has the maximum number of players.',
        'kk': 'Ойында ойыншылардың максималды саны бар.',
    },
    'joined_the_game': {
        'ru': 'Ты теперь в игре.', 'uz': 'Siz endi oʻyindasiz.',
        'tr': 'Artık oyundasın.', 'en': 'You are now in the game.', 'kk': 'Сіз енді ойындасыз.',
    },
    'join_or_leave_button': {
        'ru': 'Вступить в игру или выйти из игры', 'uz': 'Oʻyinga kirish yoki chiqish',
        'tr': 'Oyuna katıl veya oyundan çık', 'en': 'Join the game or leave the game',
        'kk': 'Ойынға кіру немесе ойыннан шығу',
    },
    'no_players_yet': {
        'ru': 'Игроков нет.', 'uz': 'Hali oʻyinchi yoʻq.', 'tr': 'Henüz oyuncu yok.',
        'en': 'No players yet.', 'kk': 'Әзірге ойыншы жоқ.',
    },
    'players_list_title': {
        'ru': 'Игроки:\n', 'uz': 'Oʻyinchilar:\n', 'tr': 'Oyuncular:\n',
        'en': 'Players:\n', 'kk': 'Ойыншылар:\n',
    },
    'request_no_longer_exists': {
        'ru': 'Заявка больше не существует.', 'uz': 'Ariza endi mavjud emas.',
        'tr': 'Başvuru artık mevcut değil.', 'en': 'The request no longer exists.',
        'kk': 'Өтінім енді жоқ.',
    },
    'chat_already_has_request': {
        'ru': 'В этом чате уже есть игра!', 'uz': 'Bu chatda allaqachon oʻyin bor!',
        'tr': 'Bu sohbette zaten bir oyun var!', 'en': 'There is already a game in this chat!',
        'kk': 'Бұл чатта ойын бар болып қойды!',
    },
    'chat_game_in_progress': {
        'ru': 'В этом чате уже идёт игра!', 'uz': 'Bu chatda oʻyin allaqachon ketmoqda!',
        'tr': 'Bu sohbette zaten bir oyun sürüyor!', 'en': 'A game is already in progress in this chat!',
        'kk': 'Бұл чатта ойын әлдеқашан жүріп жатыр!',
    },
    'no_startable_request': {
        'ru': 'У тебя нет заявки на игру, которую возможно начать.',
        'uz': 'Sizda boshlash mumkin boʻlgan oʻyin arizasi yoʻq.',
        'tr': 'Başlatabileceğin bir oyun başvurun yok.',
        'en': 'You do not have a startable game request.',
        'kk': 'Сізде бастауға болатын ойын өтінімі жоқ.',
    },
    'request_deleted': {
        'ru': 'Твоя заявка удалена.', 'uz': 'Sizning arizangiz oʻchirildi.',
        'tr': 'Başvurun silindi.', 'en': 'Your request has been deleted.',
        'kk': 'Сіздің өтінміңіз жойылды.',
    },
    'no_request': {
        'ru': 'У тебя нет заявки на игру.', 'uz': 'Sizda oʻyin arizasi yoʻq.',
        'tr': 'Bir oyun başvurun yok.', 'en': 'You do not have a game request.',
        'kk': 'Сізде ойын өтінімі жоқ.',
    },

    # ---------- handlers.py: poll (ovoz berish) ----------
    'poll_already_running': {
        'ru': 'В этом чате уже идёт голосование!', 'uz': 'Bu chatda ovoz berish allaqachon ketmoqda!',
        'tr': 'Bu sohbette zaten bir oylama sürüyor!', 'en': 'A vote is already in progress in this chat!',
        'kk': 'Бұл чатта дауыс беру әлдеқашан жүріп жатыр!',
    },
    'vote_button': {
        'ru': 'Проголосовать', 'uz': 'Ovoz berish', 'tr': 'Oy ver', 'en': 'Vote', 'kk': 'Дауыс беру',
    },
    'poll_suggestion_text': {
        'ru': '{creator} предлагает {suggestion}.', 'uz': '{creator} {suggestion}ni taklif qilyapti.',
        'tr': '{creator} {suggestion} öneriyor.', 'en': '{creator} suggests to {suggestion}.',
        'kk': '{creator} {suggestion} ұсынып жатыр.',
    },
    'poll_suggestion_end': {
        'ru': 'закончить игру', 'uz': 'oʻyinni tugatishni', 'tr': 'oyunu bitirmeyi',
        'en': 'end the game', 'kk': 'ойынды аяқтауды',
    },
    'poll_suggestion_skip': {
        'ru': 'пропустить текущую стадию', 'uz': 'joriy bosqichni oʻtkazib yuborishni',
        'tr': 'mevcut aşamayı atlamayı', 'en': 'skip the current stage',
        'kk': 'ағымдағы кезеңді өткізіп жіберуді',
    },
    'poll_no_longer_exists': {
        'ru': 'Голосование больше не существует.', 'uz': 'Ovoz berish endi mavjud emas.',
        'tr': 'Oylama artık mevcut değil.', 'en': 'The vote no longer exists.',
        'kk': 'Дауыс беру енді жоқ.',
    },
    'vote_already_counted': {
        'ru': 'Твой голос уже был учтён.', 'uz': 'Sizning ovozingiz allaqachon hisobga olingan.',
        'tr': 'Oyun zaten sayıldı.', 'en': 'Your vote has already been counted.',
        'kk': 'Сіздің дауысыңыз есепке алынды.',
    },
    'game_ended_by_vote': {
        'ru': 'Игроки проголосовали за окончание игры.',
        'uz': 'Oʻyinchilar oʻyinni tugatishga ovoz berishdi.',
        'tr': 'Oyuncular oyunu bitirmek için oy verdi.',
        'en': 'Players voted to end the game.',
        'kk': 'Ойыншылар ойынды аяқтауға дауыс берді.',
    },
    'vote_counted': {
        'ru': 'Голос учтён.', 'uz': 'Ovoz hisobga olindi.', 'tr': 'Oy sayıldı.',
        'en': 'Vote counted.', 'kk': 'Дауыс есепке алынды.',
    },

    # ---------- handlers.py: otish (shooting) ----------
    'shot_fired_at': {
        'ru': 'Выстрел произведён в игрока {number}', 'uz': '{number}-oʻyinchiga oʻq uzildi',
        'tr': '{number} numaralı oyuncuya ateş edildi', 'en': 'A shot was fired at player {number}',
        'kk': '{number}-ойыншыға оқ атылды',
    },
    'cant_participate_in_shooting': {
        'ru': 'Ты не можешь участвовать в стрельбе', 'uz': 'Siz otishda ishtirok eta olmaysiz',
        'tr': 'Ateş etmeye katılamazsın', 'en': 'You cannot participate in the shooting',
        'kk': 'Сіз атуға қатыса алмайсыз',
    },

    # ---------- handlers.py: admin ----------
    'games_db_reset': {
        'ru': 'База игр сброшена!', 'uz': "O'yinlar bazasi tozalandi!",
        'tr': 'Oyun veritabanı sıfırlandı!', 'en': 'Games database has been reset!',
        'kk': 'Ойындар базасы тазаланды!',
    },
    'games_db_printed': {
        'ru': 'Все документы базы данных игр выведены в терминал!',
        'uz': "O'yinlar bazasining barcha hujjatlari terminalga chiqarildi!",
        'tr': 'Oyun veritabanının tüm belgeleri terminale yazdırıldı!',
        'en': 'All game database documents have been printed to the terminal!',
        'kk': 'Ойындар базасының барлық құжаттары терминалға шығарылды!',
    },

    # ---------- croco.py ----------
    'croco_cant_name_own_word': {
        'ru': 'Игра окончена! Нельзя самому называть слово!',
        'uz': "Oʻyin tugadi! Soʻzni oʻzingiz aytolmaysiz!",
        'tr': 'Oyun bitti! Kelimeyi kendin söyleyemezsin!',
        'en': "Game over! You can't say the word yourself!",
        'kk': 'Ойын аяқталды! Сөзді өзің айта алмайсың!',
    },
    'croco_correct_word': {
        'ru': 'Игра окончена! Это верное слово!', 'uz': "Oʻyin tugadi! Bu toʻgʻri soʻz!",
        'tr': 'Oyun bitti! Bu doğru kelime!', 'en': 'Game over! That is the correct word!',
        'kk': 'Ойын аяқталды! Бұл дұрыс сөз!',
    },

    # ---------- gallows.py ----------
    'gallows_won': {
        'ru': 'Вы победили!', 'uz': 'Siz yutdingiz!', 'tr': 'Kazandınız!',
        'en': 'You won!', 'kk': 'Сіз жеңдіңіз!',
    },
    'gallows_lost': {
        'ru': 'Вы проиграли.', 'uz': 'Siz yutqazdingiz.', 'tr': 'Kaybettiniz.',
        'en': 'You lost.', 'kk': 'Сіз ұттыңыз.',
    },
    'letter_already_chosen': {
        'ru': 'Эта буква уже выбиралась.', 'uz': 'Bu harf allaqachon tanlangan.',
        'tr': 'Bu harf zaten seçildi.', 'en': 'This letter has already been chosen.',
        'kk': 'Бұл әріп бұрын таңдалған.',
    },

    # ---------- app.py ----------
    'minute_left_warning': {
        'ru': '{name}, до конца игры осталась минута!',
        'uz': '{name}, oʻyin tugashiga bir daqiqa qoldi!',
        'tr': '{name}, oyunun bitmesine bir dakika kaldı!',
        'en': '{name}, one minute left until the game ends!',
        'kk': '{name}, ойынның аяқталуына бір минут қалды!',
    },
    'croco_game_lost_word_was': {
        'ru': 'Игра окончена! {name} проигрывает, загаданное слово было {word}.',
        'uz': 'Oʻyin tugadi! {name} yutqazdi, yashiringan soʻz {word} edi.',
        'tr': 'Oyun bitti! {name} kaybediyor, kelime {word} idi.',
        'en': 'Game over! {name} loses, the word was {word}.',
        'kk': 'Ойын аяқталды! {name} ұтылды, жасырылған сөз {word} болатын.',
    },

    # ---------- /til buyrug'i ----------
    'language_changed': {
        'ru': 'Язык изменён на: {language}', 'uz': 'Til oʻzgartirildi: {language}',
        'tr': 'Dil değiştirildi: {language}', 'en': 'Language changed to: {language}',
        'kk': 'Тіл өзгертілді: {language}',
    },
    'language_usage': {
        'ru': 'Формат: /til <код>\nДоступные языки: {languages}',
        'uz': 'Format: /til <kod>\nMavjud tillar: {languages}',
        'tr': 'Format: /til <kod>\nMevcut diller: {languages}',
        'en': 'Format: /til <code>\nAvailable languages: {languages}',
        'kk': 'Формат: /til <код>\nҚолжетімді тілдер: {languages}',
    },
}
