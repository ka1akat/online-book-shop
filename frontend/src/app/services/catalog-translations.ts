// Переводы для расширенного каталога (книги P-1006 … P-1027 из backend/shop/catalog_data.py):
// названия, авторы, категории с описаниями, жанры, издания и аннотации.
// LanguageService подмешивает их к своим словарям.

type Names = Record<string, { en: string; ru: string; kk: string }>;

export const CATALOG_BOOK_TITLES: Names = {
  'The 7 Habits of Highly Effective People': { en: 'The 7 Habits of Highly Effective People', ru: '7 навыков высокоэффективных людей', kk: 'Тиімді адамдардың 7 дағдысы' },
  'Deep Work': { en: 'Deep Work', ru: 'В работу с головой', kk: 'Терең жұмыс' },
  "Alice's Adventures in Wonderland": { en: "Alice's Adventures in Wonderland", ru: 'Алиса в Стране чудес', kk: 'Алиса ғажайыптар елінде' },
  "Charlotte's Web": { en: "Charlotte's Web", ru: 'Паутина Шарлотты', kk: 'Шарлоттаның торы' },
  'The Nomads': { en: 'The Nomads', ru: 'Кочевники', kk: 'Көшпенділер' },
  'The Day Lasts More Than a Hundred Years': { en: 'The Day Lasts More Than a Hundred Years', ru: 'И дольше века длится день', kk: 'Ғасырдан да ұзақ күн' },
  'Brave New World': { en: 'Brave New World', ru: 'О дивный новый мир', kk: 'Ғажайып жаңа әлем' },
  'Fahrenheit 451': { en: 'Fahrenheit 451', ru: '451 градус по Фаренгейту', kk: 'Фаренгейт бойынша 451 градус' },
  'The Hobbit': { en: 'The Hobbit', ru: 'Хоббит', kk: 'Хоббит' },
  'A Wizard of Earthsea': { en: 'A Wizard of Earthsea', ru: 'Волшебник Земноморья', kk: 'Жерітеңіз сиқыршысы' },
  'Pride and Prejudice': { en: 'Pride and Prejudice', ru: 'Гордость и предубеждение', kk: 'Тәкаппарлық пен соқыр сенім' },
  'Crime and Punishment': { en: 'Crime and Punishment', ru: 'Преступление и наказание', kk: 'Қылмыс пен жаза' },
  'The Master and Margarita': { en: 'The Master and Margarita', ru: 'Мастер и Маргарита', kk: 'Шебер мен Маргарита' },
  'The Hound of the Baskervilles': { en: 'The Hound of the Baskervilles', ru: 'Собака Баскервилей', kk: 'Баскервильдер иті' },
  'Murder on the Orient Express': { en: 'Murder on the Orient Express', ru: 'Убийство в «Восточном экспрессе»', kk: '«Шығыс экспресіндегі» кісі өлімі' },
  'The Da Vinci Code': { en: 'The Da Vinci Code', ru: 'Код да Винчи', kk: 'Да Винчи коды' },
  'A Brief History of Time': { en: 'A Brief History of Time', ru: 'Краткая история времени', kk: 'Уақыттың қысқаша тарихы' },
  'Cosmos': { en: 'Cosmos', ru: 'Космос', kk: 'Ғарыш' },
  'Sapiens: A Brief History of Humankind': { en: 'Sapiens: A Brief History of Humankind', ru: 'Sapiens. Краткая история человечества', kk: 'Sapiens. Адамзаттың қысқаша тарихы' },
  'Guns, Germs, and Steel': { en: 'Guns, Germs, and Steel', ru: 'Ружья, микробы и сталь', kk: 'Мылтық, микроб және болат' },
  'Rich Dad Poor Dad': { en: 'Rich Dad Poor Dad', ru: 'Богатый папа, бедный папа', kk: 'Бай әке, кедей әке' },
  'Zero to One': { en: 'Zero to One', ru: 'От нуля к единице', kk: 'Нөлден бірге' },
  'How to Win Friends and Influence People': { en: 'How to Win Friends and Influence People', ru: 'Как завоёвывать друзей и оказывать влияние на людей', kk: 'Дос табу және адамдарға ықпал ету' },
  'Winnie-the-Pooh': { en: 'Winnie-the-Pooh', ru: 'Винни-Пух', kk: 'Винни-Пух' },
  'Pippi Longstocking': { en: 'Pippi Longstocking', ru: 'Пеппи Длинныйчулок', kk: 'Ұзыншұлық Пеппи' },
  'The White Ship': { en: 'The White Ship', ru: 'Белый пароход', kk: 'Ақ кеме' },
  'Dune': { en: 'Dune', ru: 'Дюна', kk: 'Дюна' },
  'Harry Potter and the Chamber of Secrets': { en: 'Harry Potter and the Chamber of Secrets', ru: 'Гарри Поттер и Тайная комната', kk: 'Гарри Поттер және құпия бөлме' },
  'The Great Gatsby': { en: 'The Great Gatsby', ru: 'Великий Гэтсби', kk: 'Ұлы Гэтсби' },
  'War and Peace': { en: 'War and Peace', ru: 'Война и мир', kk: 'Соғыс және бейбітшілік' },
  'And Then There Were None': { en: 'And Then There Were None', ru: 'Десять негритят', kk: 'Он кішкентай үнді' },
  'The Selfish Gene': { en: 'The Selfish Gene', ru: 'Эгоистичный ген', kk: 'Өзімшіл ген' },
  'SPQR: A History of Ancient Rome': { en: 'SPQR: A History of Ancient Rome', ru: 'SPQR. История Древнего Рима', kk: 'SPQR. Ежелгі Рим тарихы' },
  'The Lean Startup': { en: 'The Lean Startup', ru: 'Бизнес с нуля. Метод Lean Startup', kk: 'Lean Startup әдісі' },
  'The Intelligent Investor': { en: 'The Intelligent Investor', ru: 'Разумный инвестор', kk: 'Ақылды инвестор' },
};

export const CATALOG_AUTHORS: Names = {
  'Stephen R. Covey': { en: 'Stephen R. Covey', ru: 'Стивен Кови', kk: 'Стивен Кови' },
  'Cal Newport': { en: 'Cal Newport', ru: 'Кэл Ньюпорт', kk: 'Кэл Ньюпорт' },
  'Lewis Carroll': { en: 'Lewis Carroll', ru: 'Льюис Кэрролл', kk: 'Льюис Кэрролл' },
  'E. B. White': { en: 'E. B. White', ru: 'Элвин Брукс Уайт', kk: 'Элвин Брукс Уайт' },
  'Ilyas Esenberlin': { en: 'Ilyas Esenberlin', ru: 'Ильяс Есенберлин', kk: 'Ілияс Есенберлин' },
  'Chingiz Aitmatov': { en: 'Chingiz Aitmatov', ru: 'Чингиз Айтматов', kk: 'Шыңғыс Айтматов' },
  'Aldous Huxley': { en: 'Aldous Huxley', ru: 'Олдос Хаксли', kk: 'Олдос Хаксли' },
  'Ray Bradbury': { en: 'Ray Bradbury', ru: 'Рэй Брэдбери', kk: 'Рэй Брэдбери' },
  'J. R. R. Tolkien': { en: 'J. R. R. Tolkien', ru: 'Дж. Р. Р. Толкин', kk: 'Дж. Р. Р. Толкин' },
  'Ursula K. Le Guin': { en: 'Ursula K. Le Guin', ru: 'Урсула Ле Гуин', kk: 'Урсула Ле Гуин' },
  'Jane Austen': { en: 'Jane Austen', ru: 'Джейн Остин', kk: 'Джейн Остин' },
  'Fyodor Dostoevsky': { en: 'Fyodor Dostoevsky', ru: 'Фёдор Достоевский', kk: 'Фёдор Достоевский' },
  'Mikhail Bulgakov': { en: 'Mikhail Bulgakov', ru: 'Михаил Булгаков', kk: 'Михаил Булгаков' },
  'Arthur Conan Doyle': { en: 'Arthur Conan Doyle', ru: 'Артур Конан Дойл', kk: 'Артур Конан Дойл' },
  'Agatha Christie': { en: 'Agatha Christie', ru: 'Агата Кристи', kk: 'Агата Кристи' },
  'Dan Brown': { en: 'Dan Brown', ru: 'Дэн Браун', kk: 'Дэн Браун' },
  'Stephen Hawking': { en: 'Stephen Hawking', ru: 'Стивен Хокинг', kk: 'Стивен Хокинг' },
  'Carl Sagan': { en: 'Carl Sagan', ru: 'Карл Саган', kk: 'Карл Саган' },
  'Yuval Noah Harari': { en: 'Yuval Noah Harari', ru: 'Юваль Ной Харари', kk: 'Юваль Ной Харари' },
  'Jared Diamond': { en: 'Jared Diamond', ru: 'Джаред Даймонд', kk: 'Джаред Даймонд' },
  'Robert T. Kiyosaki': { en: 'Robert T. Kiyosaki', ru: 'Роберт Кийосаки', kk: 'Роберт Кийосаки' },
  'Peter Thiel': { en: 'Peter Thiel', ru: 'Питер Тиль', kk: 'Питер Тиль' },
  'Dale Carnegie': { en: 'Dale Carnegie', ru: 'Дейл Карнеги', kk: 'Дейл Карнеги' },
  'A. A. Milne': { en: 'A. A. Milne', ru: 'Алан Милн', kk: 'Алан Милн' },
  'Astrid Lindgren': { en: 'Astrid Lindgren', ru: 'Астрид Линдгрен', kk: 'Астрид Линдгрен' },
  'Frank Herbert': { en: 'Frank Herbert', ru: 'Фрэнк Герберт', kk: 'Фрэнк Герберт' },
  'F. Scott Fitzgerald': { en: 'F. Scott Fitzgerald', ru: 'Фрэнсис Скотт Фицджеральд', kk: 'Фрэнсис Скотт Фицджеральд' },
  'Leo Tolstoy': { en: 'Leo Tolstoy', ru: 'Лев Толстой', kk: 'Лев Толстой' },
  'Richard Dawkins': { en: 'Richard Dawkins', ru: 'Ричард Докинз', kk: 'Ричард Докинз' },
  'Mary Beard': { en: 'Mary Beard', ru: 'Мэри Бирд', kk: 'Мэри Бирд' },
  'Eric Ries': { en: 'Eric Ries', ru: 'Эрик Рис', kk: 'Эрик Рис' },
  'Benjamin Graham': { en: 'Benjamin Graham', ru: 'Бенджамин Грэхем', kk: 'Бенджамин Грэхем' },
};

export const CATALOG_PHRASES: Record<'ru' | 'kk', Record<string, string>> = {
  ru: {
    // Категории и их описания
    'Classics': 'Классика', 'Mystery & Thriller': 'Детективы и триллеры', 'Popular Science': 'Научпоп',
    'History': 'История', 'Business': 'Бизнес',
    'Practical books about habits, focus and personal growth.': 'Практичные книги о привычках, концентрации и личном росте.',
    "Stories for young readers — and for the grown-ups who read with them.": 'Истории для юных читателей — и для взрослых, которые читают вместе с ними.',
    'Great novels of Kazakh and Central Asian writers.': 'Великие романы казахских и центральноазиатских писателей.',
    "Dystopias and science fiction that make you look at today's world differently.": 'Антиутопии и фантастика, после которых по-другому смотришь на сегодняшний мир.',
    'Magic, dragons and other worlds.': 'Магия, драконы и другие миры.',
    'World classics that every reader comes back to.': 'Мировая классика, к которой возвращается каждый читатель.',
    "Detectives, puzzles and stories you can't put down.": 'Детективы, загадки и истории, от которых невозможно оторваться.',
    'Big scientific ideas explained for everyone.': 'Большие научные идеи простым языком.',
    'How humanity got to where it is today.': 'Как человечество пришло к тому, что есть сегодня.',
    'Money, startups and how companies are built.': 'Деньги, стартапы и то, как строятся компании.',
    // Жанры
    'Productivity': 'Продуктивность', "Children's story": 'Детская повесть', 'Historical novel': 'Исторический роман',
    'Science fiction': 'Научная фантастика', 'Classic novel': 'Классический роман', 'Detective': 'Детектив',
    'Thriller': 'Триллер', 'Popular science': 'Научно-популярная литература', 'Finance': 'Финансы',
    // Сообщения сервера, которые раньше оставались на английском
    'Please log in to leave a review.': 'Войдите, чтобы оставить отзыв.',
    'Log in with this email to use a saved address.': 'Войдите с этой почтой, чтобы использовать сохранённый адрес.',
    'Log in with this email to view saved addresses.': 'Войдите с этой почтой, чтобы посмотреть сохранённые адреса.',
    'Saved address does not belong to this customer.': 'Этот сохранённый адрес принадлежит другому покупателю.',
    'We could not find this order. Please check the link or the e-mail.': 'Мы не нашли этот заказ. Проверьте ссылку или почту.',
    'Please enter the e-mail that was used for the order.': 'Укажите почту, на которую оформлен заказ.',
    'Order is required.': 'Укажите заказ.',
    'Must be a number.': 'Должно быть числом.',
    'Cannot be negative.': 'Не может быть отрицательным.',
    // Заказ, оплата и возврат (backend/shop/services.py)
    'Please enter a delivery address.': 'Укажите адрес доставки.',
    'Quantity must be 1 or more.': 'Количество должно быть 1 или больше.',
    'The card number must have 16 digits.': 'Номер карты должен состоять из 16 цифр.',
    'This order has already been paid.': 'Этот заказ уже оплачен.',
    'The reservation has expired (15 minutes). Please place the order again.': 'Бронь истекла (15 минут). Оформите заказ заново.',
    'The bank declined the payment: insufficient funds. Please try another card.': 'Банк отклонил оплату: недостаточно средств. Попробуйте другую карту.',
    'Please choose a refund reason.': 'Укажите причину возврата.',
    'Payment not found.': 'Платёж не найден.',
    'This payment has already been refunded.': 'Этот платёж уже возвращён.',
    'Only a successful payment can be refunded.': 'Вернуть можно только успешный платёж.',
    'Only a paid order can be refunded.': 'Вернуть можно только оплаченный заказ.',
    // Требования к паролю (стандартные сообщения Django)
    'This password is too short.': 'Пароль слишком короткий.',
    'It must contain at least 8 characters.': 'Он должен содержать не менее 8 символов.',
    'This password is too common.': 'Этот пароль слишком распространён.',
    'This password is entirely numeric.': 'Пароль не может состоять только из цифр.',
    'The password is too similar to the username.': 'Пароль слишком похож на имя пользователя.',
    'The password is too similar to the email address.': 'Пароль слишком похож на адрес почты.',
    'The password is too similar to the first name.': 'Пароль слишком похож на имя.',
    // Издания
    'Paperback edition': 'Мягкая обложка', 'Hardcover edition': 'Твёрдая обложка',
    'Illustrated hardcover edition': 'Иллюстрированное издание в твёрдой обложке',
    'Trilogy; page count varies by edition': 'Трилогия; число страниц зависит от издания',
    // Аннотации
    'Stephen Covey describes seven habits that move a person from dependence to independence and then to working well with others. Instead of quick tricks, the book focuses on values, priorities and long-term character.':
      'Стивен Кови описывает семь навыков, которые ведут человека от зависимости к самостоятельности, а затем к умению работать вместе с другими. Вместо быстрых приёмов книга говорит о ценностях, приоритетах и характере.',
    'Cal Newport argues that the ability to concentrate without distraction is becoming rare and valuable. He explains how to plan focused work, cut down on shallow tasks and train attention like a skill.':
      'Кэл Ньюпорт утверждает, что умение сосредоточиться без отвлечений становится редким и ценным. Он объясняет, как планировать глубокую работу, сокращать поверхностные задачи и тренировать внимание как навык.',
    'Alice follows a White Rabbit down a rabbit hole and finds herself in a strange world of talking animals, a Mad Hatter\'s tea party and a Queen who shouts "Off with their heads!". A playful story full of wordplay and nonsense.':
      'Алиса прыгает в кроличью нору вслед за Белым Кроликом и попадает в странный мир говорящих животных, безумного чаепития у Шляпника и Королевы, которая кричит: «Отрубить им головы!». Весёлая сказка, полная игры слов и чепухи.',
    'Wilbur the pig is saved from an early end by his friend Charlotte, a clever spider who writes words in her web. A warm story about friendship, loyalty and growing up.':
      'Поросёнка Уилбура спасает его подруга Шарлотта — умная паучиха, которая пишет слова в своей паутине. Тёплая история о дружбе, верности и взрослении.',
    'An epic trilogy about the history of the Kazakh Khanate — from its founding to the struggle for independence. Khans, warriors and ordinary people of the steppe live through centuries of wars, alliances and hope.':
      'Эпическая трилогия об истории Казахского ханства — от его основания до борьбы за независимость. Ханы, батыры и простые люди степи проходят через века войн, союзов и надежд.',
    'A railway worker at a remote steppe junction travels across the desert to bury an old friend. His journey mixes memories of his life, the ancient legend of the mankurt and a story about contact with another civilisation.':
      'Железнодорожник с далёкого степного разъезда везёт через пустыню хоронить старого друга. В его пути переплетаются воспоминания о жизни, древняя легенда о манкурте и история о контакте с другой цивилизацией.',
    'In the World State people are made in laboratories, sorted into castes and kept happy with entertainment and a drug called soma. When an outsider arrives from a reservation, the perfect society starts to look less perfect.':
      'В Мировом Государстве людей выращивают в лабораториях, делят на касты и делают счастливыми с помощью развлечений и наркотика сомы. Когда из резервации приезжает чужак, идеальное общество начинает выглядеть не таким уж идеальным.',
    'Guy Montag is a fireman whose job is to burn books. After meeting a curious young neighbour he begins to question his work and secretly reads the books he should destroy.':
      'Гай Монтэг — пожарный, чья работа — сжигать книги. После встречи с любознательной юной соседкой он начинает сомневаться в своём деле и тайком читает книги, которые должен уничтожать.',
    "Bilbo Baggins, a hobbit who loves a quiet life, is pulled into an adventure with a wizard and thirteen dwarves. On the way to a dragon's treasure he meets trolls, elves and a creature named Gollum.":
      'Бильбо Бэггинс, хоббит, любящий спокойную жизнь, отправляется в приключение с волшебником и тринадцатью гномами. По пути к сокровищам дракона он встречает троллей, эльфов и существо по имени Голлум.',
    'A gifted boy named Ged goes to a school of wizards and, out of pride, releases a dark shadow into the world. To survive he must stop running and face it.':
      'Одарённый мальчик Гед поступает в школу волшебников и из гордости выпускает в мир тёмную тень. Чтобы выжить, ему придётся перестать убегать и встретиться с ней лицом к лицу.',
    'Elizabeth Bennet is clever, quick and not afraid to speak her mind. Her meetings with the proud Mr Darcy turn into a story about first impressions, family and changing your opinion.':
      'Элизабет Беннет умна, остра на язык и не боится говорить, что думает. Её встречи с гордым мистером Дарси превращаются в историю о первом впечатлении, семье и умении изменить своё мнение.',
    'A poor former student in St Petersburg commits a crime, convinced that some people stand above ordinary rules. The novel follows his fear, guilt and the inner struggle that comes after.':
      'Бедный бывший студент в Петербурге совершает преступление, уверенный, что некоторые люди стоят выше обычных правил. Роман прослеживает его страх, вину и внутреннюю борьбу после этого.',
    'A mysterious foreign professor and his strange companions arrive in 1930s Moscow and turn the city upside down. Alongside runs the story of a writer, the woman who loves him and his novel about Pontius Pilate.':
      'Таинственный иностранный профессор и его странная свита появляются в Москве 1930-х и переворачивают город вверх дном. Параллельно идёт история писателя, любящей его женщины и его романа о Понтии Пилате.',
    'A legend about a giant hound haunts the Baskerville family on the moors of Devon. Sherlock Holmes and Dr Watson must find out whether the danger is supernatural or very human.':
      'Легенда о гигантской собаке преследует семью Баскервилей на болотах Девоншира. Шерлок Холмс и доктор Ватсон должны выяснить, сверхъестественная ли это опасность или вполне человеческая.',
    'A snowdrift stops the famous train, and in the morning one of the passengers is found dead. Detective Hercule Poirot has a carriage full of suspects — and each of them has an alibi.':
      'Снежный занос останавливает знаменитый поезд, а утром одного из пассажиров находят мёртвым. У Эркюля Пуаро целый вагон подозреваемых — и у каждого есть алиби.',
    'A murder in the Louvre leaves behind a trail of codes hidden in famous works of art. Professor Robert Langdon and cryptologist Sophie Neveu race across Paris and London to solve the puzzle.':
      'Убийство в Лувре оставляет след из шифров, спрятанных в знаменитых произведениях искусства. Профессор Роберт Лэнгдон и криптограф Софи Невё мчатся через Париж и Лондон, чтобы разгадать загадку.',
    'Stephen Hawking explains the Big Bang, black holes and the nature of time with almost no formulas. A classic introduction to how physicists think about the universe.':
      'Стивен Хокинг почти без формул объясняет Большой взрыв, чёрные дыры и природу времени. Классическое введение в то, как физики думают о Вселенной.',
    'Carl Sagan takes the reader on a journey from the origin of life on Earth to distant galaxies. The book tells the story of science and of the people who made its discoveries.':
      'Карл Саган отправляет читателя в путешествие от зарождения жизни на Земле до далёких галактик. Книга рассказывает историю науки и людей, которые совершили её открытия.',
    'How did one ordinary species of human come to rule the planet? Harari walks through the cognitive, agricultural and scientific revolutions and asks what they mean for our happiness.':
      'Как один ничем не примечательный вид людей стал хозяином планеты? Харари проходит через когнитивную, аграрную и научную революции и спрашивает, что они значат для нашего счастья.',
    'Why did some societies develop writing, technology and empires earlier than others? Jared Diamond looks for the answer in geography, farming and the spread of diseases.':
      'Почему одни общества раньше других создали письменность, технологии и империи? Джаред Даймонд ищет ответ в географии, земледелии и распространении болезней.',
    'The author compares the money lessons of his two "dads" — his own father and his best friend\'s father. A simple book about assets, liabilities and why financial literacy matters.':
      'Автор сравнивает уроки о деньгах от двух «пап» — родного отца и отца лучшего друга. Простая книга об активах, пассивах и о том, почему важна финансовая грамотность.',
    'Peter Thiel explains why the best startups create something truly new instead of copying what already exists. Notes on monopolies, founders and thinking about the future.':
      'Питер Тиль объясняет, почему лучшие стартапы создают что-то действительно новое, а не копируют уже существующее. Заметки о монополиях, основателях и мышлении о будущем.',
    'Dale Carnegie shares simple rules for talking to people, making a good impression and solving conflicts without arguments. One of the best-known books about communication.':
      'Дейл Карнеги делится простыми правилами: как разговаривать с людьми, производить хорошее впечатление и решать конфликты без споров. Одна из самых известных книг об общении.',
    'A bear of very little brain, his friend Piglet and the other animals of the Hundred Acre Wood go looking for honey, hunt for Heffalumps and celebrate birthdays. Gentle stories for reading aloud.':
      'Медвежонок с опилками в голове, его друг Пятачок и другие жители Стоакрового леса ищут мёд, охотятся на Слонопотама и празднуют дни рождения. Добрые истории для чтения вслух.',
    'Pippi is nine, lives alone with a horse and a monkey and is the strongest girl in the world. Her neighbours Tommy and Annika discover that life next to Pippi is never boring.':
      'Пеппи девять лет, она живёт одна с лошадью и обезьянкой и она самая сильная девочка на свете. Её соседи Томми и Анника узнают, что рядом с Пеппи никогда не бывает скучно.',
    'A lonely boy lives with his grandfather at a forest outpost in the mountains and believes in the legend of the Horned Mother Deer. He dreams of turning into a fish and swimming to the white ship where his father may be.':
      'Одинокий мальчик живёт с дедом на лесном кордоне в горах и верит в легенду о Рогатой матери-оленихе. Он мечтает превратиться в рыбу и доплыть до белого парохода, на котором, может быть, плавает его отец.',
    'Young Paul Atreides moves with his family to the desert planet Arrakis, the only source of the most valuable substance in the universe. Betrayal forces him to survive among the desert people and discover his own destiny.':
      'Юный Пол Атрейдес вместе с семьёй переезжает на пустынную планету Арракис — единственный источник самого ценного вещества во Вселенной. Предательство заставляет его выживать среди людей пустыни и открыть своё предназначение.',
    'In his second year at Hogwarts Harry hears a mysterious voice in the walls, and students are found turned to stone. Harry, Ron and Hermione try to find out who has opened the legendary Chamber of Secrets.':
      'На втором курсе Хогвартса Гарри слышит таинственный голос в стенах, а учеников находят окаменевшими. Гарри, Рон и Гермиона пытаются узнать, кто открыл легендарную Тайную комнату.',
    'Nick Carraway moves next door to the mysterious millionaire Jay Gatsby, famous for his huge parties. Behind the glamour of the 1920s lies a story of love, ambition and the American dream.':
      'Ник Каррауэй поселяется по соседству с таинственным миллионером Джеем Гэтсби, известным своими роскошными вечеринками. За блеском 1920-х скрывается история о любви, амбициях и американской мечте.',
    'Several noble families live through the Napoleonic wars in Russia. Battles, balls and quiet family scenes come together in a great novel about history, love and the meaning of life.':
      'Несколько дворянских семей переживают эпоху наполеоновских войн в России. Сражения, балы и тихие семейные сцены складываются в великий роман об истории, любви и смысле жизни.',
    'Ten strangers are invited to a lonely island, and the host never arrives. One by one the guests begin to die, and they understand that the killer is one of them.':
      'Десять незнакомцев приглашены на уединённый остров, но хозяин так и не появляется. Гости начинают умирать один за другим и понимают, что убийца — один из них.',
    'Richard Dawkins looks at evolution from the point of view of genes. The book explains how cooperation and even kindness between animals can come from natural selection.':
      'Ричард Докинз смотрит на эволюцию с точки зрения генов. Книга объясняет, как сотрудничество и даже доброта между животными могут возникать благодаря естественному отбору.',
    'Mary Beard tells how a small town on the Tiber became the centre of a huge empire. The book shows not only emperors and wars but also the everyday life of ordinary Romans.':
      'Мэри Бирд рассказывает, как небольшой город на Тибре стал центром огромной империи. В книге не только императоры и войны, но и повседневная жизнь простых римлян.',
    'Eric Ries explains how to build a startup step by step: make a simple product, test it with real customers and learn quickly from the results instead of guessing.':
      'Эрик Рис объясняет, как строить стартап шаг за шагом: сделать простой продукт, проверить его на настоящих клиентах и быстро учиться на результатах, а не гадать.',
    'Benjamin Graham describes value investing: how to buy shares carefully, protect yourself from big losses and not follow the emotions of the market. A classic book about long-term investing.':
      'Бенджамин Грэхем описывает стоимостное инвестирование: как осторожно покупать акции, защищаться от больших потерь и не поддаваться эмоциям рынка. Классическая книга о долгосрочных инвестициях.',
  },
  kk: {
    'Classics': 'Классика', 'Mystery & Thriller': 'Детективтер мен триллерлер', 'Popular Science': 'Ғылыми-көпшілік',
    'History': 'Тарих', 'Business': 'Бизнес',
    'Productivity': 'Өнімділік', "Children's story": 'Балалар хикаясы', 'Historical novel': 'Тарихи роман',
    'Science fiction': 'Ғылыми фантастика', 'Classic novel': 'Классикалық роман', 'Detective': 'Детектив',
    'Thriller': 'Триллер', 'Popular science': 'Ғылыми-көпшілік әдебиет', 'Finance': 'Қаржы',
    'Paperback edition': 'Жұмсақ мұқабалы басылым', 'Hardcover edition': 'Қатты мұқабалы басылым',
    'Illustrated hardcover edition': 'Суретті, қатты мұқабалы басылым',
    'Trilogy; page count varies by edition': 'Трилогия; бет саны басылымға байланысты',
  },
};
