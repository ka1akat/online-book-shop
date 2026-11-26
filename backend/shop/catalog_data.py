"""Demo catalog: categories and books.

One source of truth for the demo data:
  * `python manage.py seed_books` loads everything from here (local database);
  * migration 0024_more_books adds the books that are missing (server database on Render,
    where build.sh runs seed_books only once, into an empty database).
"""

# category name -> short description (shown on the catalog page when the category is selected)
CATEGORIES = {
    "Personal Development": "Practical books about habits, focus and personal growth.",
    "Children's Books": "Stories for young readers — and for the grown-ups who read with them.",
    "Literature": "Great novels of Kazakh and Central Asian writers.",
    "Fiction": "Dystopias and science fiction that make you look at today's world differently.",
    "Fantasy": "Magic, dragons and other worlds.",
    "Classics": "World classics that every reader comes back to.",
    "Mystery & Thriller": "Detectives, puzzles and stories you can't put down.",
    "Popular Science": "Big scientific ideas explained for everyone.",
    "History": "How humanity got to where it is today.",
    "Business": "Money, startups and how companies are built.",
}

# Every book: product_id is the primary key (format P-1001, max 6 characters).
BOOKS = [
    # ---------- The original five demo books ----------
    {
        "product_id": "P-1001", "product_name": "Atomic Habits", "author": "James Clear",
        "genre": "Self-development", "category": "Personal Development", "price": 6500, "stock": 0,
        "year": 2018, "pages": 320, "edition": "Avery hardcover edition", "languages": ["English"],
        "description": "James Clear explains how small routines can build into lasting change. The book follows a practical four-step framework—make it obvious, attractive, easy, and satisfying—to help readers build helpful habits and reduce unwanted ones. It combines research from biology, psychology, and neuroscience with everyday examples and exercises for shaping routines and the environment around them.",
    },
    {
        "product_id": "P-1002", "product_name": "The Little Prince", "author": "Antoine de Saint-Exupery",
        "genre": "Fairy tale", "category": "Children's Books", "price": 3000, "stock": 25,
        "year": 1943, "pages": 96, "edition": "Penguin Random House hardcover edition", "languages": ["English", "Russian"],
        "description": "A pilot makes an emergency landing in the Sahara and meets a mysterious boy from a tiny asteroid. As the Little Prince tells the story of his travels and the people he met on other planets, the pilot learns about the prince's rose and his journey to Earth. Their friendship frames a fable about seeing beyond appearances, caring for others, and understanding what matters.",
    },
    {
        "product_id": "P-1003", "product_name": "Abai Zholy", "author": "Mukhtar Auezov",
        "genre": "Novel", "category": "Literature", "price": 4500, "stock": 8,
        "year": 1942, "pages": None, "edition": "Four-part epic; page count varies by edition", "languages": ["Kazakh", "Russian"],
        "description": "This historical novel follows Abai from childhood into adulthood on the Kazakh steppe. Through his relationships with family, poets, and community leaders, the story depicts the traditions, conflicts, and social changes of nineteenth-century Kazakh society. The work is an epic published in multiple books and volumes; the total page count depends on the edition.",
    },
    {
        "product_id": "P-1004", "product_name": "1984", "author": "George Orwell",
        "genre": "Dystopia", "category": "Fiction", "price": 5000, "stock": 7,
        "year": 1949, "pages": 352, "edition": "Signet mass-market paperback edition", "languages": ["English", "Russian"],
        "description": "Winston Smith works at the Ministry of Truth, where he alters old records to match the ruling Party's version of events. In a society shaped by surveillance, propaganda, and fear, he begins a private diary and forms a forbidden relationship with Julia. His search for truth and personal freedom brings him into conflict with the system that controls everyday life.",
    },
    {
        "product_id": "P-1005", "product_name": "Harry Potter and the Sorcerer's Stone", "author": "J. K. Rowling",
        "genre": "Fantasy", "category": "Fantasy", "price": 7000, "stock": 15,
        "year": 1997, "pages": 336, "edition": "Scholastic paperback edition (Sorcerer's Stone title)", "languages": ["English", "Russian"],
        "description": "On his eleventh birthday, Harry Potter discovers that he is a wizard and leaves his unhappy home to study at Hogwarts. He makes friends with Ron and Hermione, learns about his parents, and encounters a mystery surrounding the Sorcerer's Stone. The first story follows Harry through his first year at the school as he and his friends try to uncover what is being hidden.",
    },
    # ---------- Personal Development ----------
    {
        "product_id": "P-1006", "product_name": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey",
        "genre": "Self-development", "category": "Personal Development", "price": 7200, "stock": 12,
        "year": 1989, "pages": 432, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Stephen Covey describes seven habits that move a person from dependence to independence and then to working well with others. Instead of quick tricks, the book focuses on values, priorities and long-term character.",
    },
    {
        "product_id": "P-1007", "product_name": "Deep Work", "author": "Cal Newport",
        "genre": "Productivity", "category": "Personal Development", "price": 6200, "stock": 6,
        "year": 2016, "pages": 304, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Cal Newport argues that the ability to concentrate without distraction is becoming rare and valuable. He explains how to plan focused work, cut down on shallow tasks and train attention like a skill.",
    },
    # ---------- Children's Books ----------
    {
        "product_id": "P-1008", "product_name": "Alice's Adventures in Wonderland", "author": "Lewis Carroll",
        "genre": "Fairy tale", "category": "Children's Books", "price": 3500, "stock": 18,
        "year": 1865, "pages": 192, "edition": "Illustrated hardcover edition", "languages": ["English", "Russian"],
        "description": "Alice follows a White Rabbit down a rabbit hole and finds herself in a strange world of talking animals, a Mad Hatter's tea party and a Queen who shouts \"Off with their heads!\". A playful story full of wordplay and nonsense.",
    },
    {
        "product_id": "P-1009", "product_name": "Charlotte's Web", "author": "E. B. White",
        "genre": "Children's story", "category": "Children's Books", "price": 3800, "stock": 9,
        "year": 1952, "pages": 192, "edition": "Paperback edition", "languages": ["English"],
        "description": "Wilbur the pig is saved from an early end by his friend Charlotte, a clever spider who writes words in her web. A warm story about friendship, loyalty and growing up.",
    },
    # ---------- Literature ----------
    {
        "product_id": "P-1010", "product_name": "The Nomads", "author": "Ilyas Esenberlin",
        "genre": "Historical novel", "category": "Literature", "price": 5800, "stock": 5,
        "year": 1976, "pages": None, "edition": "Trilogy; page count varies by edition", "languages": ["Kazakh", "Russian"],
        "description": "An epic trilogy about the history of the Kazakh Khanate — from its founding to the struggle for independence. Khans, warriors and ordinary people of the steppe live through centuries of wars, alliances and hope.",
    },
    {
        "product_id": "P-1011", "product_name": "The Day Lasts More Than a Hundred Years", "author": "Chingiz Aitmatov",
        "genre": "Novel", "category": "Literature", "price": 4900, "stock": 0,
        "year": 1980, "pages": 352, "edition": "Paperback edition", "languages": ["Russian", "Kazakh"],
        "description": "A railway worker at a remote steppe junction travels across the desert to bury an old friend. His journey mixes memories of his life, the ancient legend of the mankurt and a story about contact with another civilisation.",
    },
    # ---------- Fiction ----------
    {
        "product_id": "P-1012", "product_name": "Brave New World", "author": "Aldous Huxley",
        "genre": "Dystopia", "category": "Fiction", "price": 5200, "stock": 11,
        "year": 1932, "pages": 288, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "In the World State people are made in laboratories, sorted into castes and kept happy with entertainment and a drug called soma. When an outsider arrives from a reservation, the perfect society starts to look less perfect.",
    },
    {
        "product_id": "P-1013", "product_name": "Fahrenheit 451", "author": "Ray Bradbury",
        "genre": "Science fiction", "category": "Fiction", "price": 4600, "stock": 14,
        "year": 1953, "pages": 256, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Guy Montag is a fireman whose job is to burn books. After meeting a curious young neighbour he begins to question his work and secretly reads the books he should destroy.",
    },
    # ---------- Fantasy ----------
    {
        "product_id": "P-1014", "product_name": "The Hobbit", "author": "J. R. R. Tolkien",
        "genre": "Fantasy", "category": "Fantasy", "price": 6800, "stock": 10,
        "year": 1937, "pages": 310, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Bilbo Baggins, a hobbit who loves a quiet life, is pulled into an adventure with a wizard and thirteen dwarves. On the way to a dragon's treasure he meets trolls, elves and a creature named Gollum.",
    },
    {
        "product_id": "P-1015", "product_name": "A Wizard of Earthsea", "author": "Ursula K. Le Guin",
        "genre": "Fantasy", "category": "Fantasy", "price": 5400, "stock": 4,
        "year": 1968, "pages": 183, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "A gifted boy named Ged goes to a school of wizards and, out of pride, releases a dark shadow into the world. To survive he must stop running and face it.",
    },
    # ---------- Classics ----------
    {
        "product_id": "P-1016", "product_name": "Pride and Prejudice", "author": "Jane Austen",
        "genre": "Classic novel", "category": "Classics", "price": 4200, "stock": 16,
        "year": 1813, "pages": 432, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Elizabeth Bennet is clever, quick and not afraid to speak her mind. Her meetings with the proud Mr Darcy turn into a story about first impressions, family and changing your opinion.",
    },
    {
        "product_id": "P-1017", "product_name": "Crime and Punishment", "author": "Fyodor Dostoevsky",
        "genre": "Classic novel", "category": "Classics", "price": 5600, "stock": 8,
        "year": 1866, "pages": 576, "edition": "Paperback edition", "languages": ["Russian", "English"],
        "description": "A poor former student in St Petersburg commits a crime, convinced that some people stand above ordinary rules. The novel follows his fear, guilt and the inner struggle that comes after.",
    },
    {
        "product_id": "P-1018", "product_name": "The Master and Margarita", "author": "Mikhail Bulgakov",
        "genre": "Classic novel", "category": "Classics", "price": 5900, "stock": 13,
        "year": 1967, "pages": 448, "edition": "Paperback edition", "languages": ["Russian", "English"],
        "description": "A mysterious foreign professor and his strange companions arrive in 1930s Moscow and turn the city upside down. Alongside runs the story of a writer, the woman who loves him and his novel about Pontius Pilate.",
    },
    # ---------- Mystery & Thriller ----------
    {
        "product_id": "P-1019", "product_name": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle",
        "genre": "Detective", "category": "Mystery & Thriller", "price": 3900, "stock": 20,
        "year": 1902, "pages": 256, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "A legend about a giant hound haunts the Baskerville family on the moors of Devon. Sherlock Holmes and Dr Watson must find out whether the danger is supernatural or very human.",
    },
    {
        "product_id": "P-1020", "product_name": "Murder on the Orient Express", "author": "Agatha Christie",
        "genre": "Detective", "category": "Mystery & Thriller", "price": 4400, "stock": 7,
        "year": 1934, "pages": 256, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "A snowdrift stops the famous train, and in the morning one of the passengers is found dead. Detective Hercule Poirot has a carriage full of suspects — and each of them has an alibi.",
    },
    {
        "product_id": "P-1021", "product_name": "The Da Vinci Code", "author": "Dan Brown",
        "genre": "Thriller", "category": "Mystery & Thriller", "price": 5300, "stock": 3,
        "year": 2003, "pages": 489, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "A murder in the Louvre leaves behind a trail of codes hidden in famous works of art. Professor Robert Langdon and cryptologist Sophie Neveu race across Paris and London to solve the puzzle.",
    },
    # ---------- Popular Science ----------
    {
        "product_id": "P-1022", "product_name": "A Brief History of Time", "author": "Stephen Hawking",
        "genre": "Popular science", "category": "Popular Science", "price": 6100, "stock": 9,
        "year": 1988, "pages": 212, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Stephen Hawking explains the Big Bang, black holes and the nature of time with almost no formulas. A classic introduction to how physicists think about the universe.",
    },
    {
        "product_id": "P-1023", "product_name": "Cosmos", "author": "Carl Sagan",
        "genre": "Popular science", "category": "Popular Science", "price": 6900, "stock": 0,
        "year": 1980, "pages": 396, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Carl Sagan takes the reader on a journey from the origin of life on Earth to distant galaxies. The book tells the story of science and of the people who made its discoveries.",
    },
    # ---------- History ----------
    {
        "product_id": "P-1024", "product_name": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari",
        "genre": "History", "category": "History", "price": 7500, "stock": 15,
        "year": 2011, "pages": 464, "edition": "Paperback edition", "languages": ["English", "Russian", "Kazakh"],
        "description": "How did one ordinary species of human come to rule the planet? Harari walks through the cognitive, agricultural and scientific revolutions and asks what they mean for our happiness.",
    },
    {
        "product_id": "P-1025", "product_name": "Guns, Germs, and Steel", "author": "Jared Diamond",
        "genre": "History", "category": "History", "price": 7300, "stock": 5,
        "year": 1997, "pages": 480, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Why did some societies develop writing, technology and empires earlier than others? Jared Diamond looks for the answer in geography, farming and the spread of diseases.",
    },
    # ---------- Business ----------
    {
        "product_id": "P-1026", "product_name": "Rich Dad Poor Dad", "author": "Robert T. Kiyosaki",
        "genre": "Finance", "category": "Business", "price": 5000, "stock": 22,
        "year": 1997, "pages": 336, "edition": "Paperback edition", "languages": ["English", "Russian", "Kazakh"],
        "description": "The author compares the money lessons of his two \"dads\" — his own father and his best friend's father. A simple book about assets, liabilities and why financial literacy matters.",
    },
    {
        "product_id": "P-1027", "product_name": "Zero to One", "author": "Peter Thiel",
        "genre": "Business", "category": "Business", "price": 6400, "stock": 6,
        "year": 2014, "pages": 224, "edition": "Hardcover edition", "languages": ["English", "Russian"],
        "description": "Peter Thiel explains why the best startups create something truly new instead of copying what already exists. Notes on monopolies, founders and thinking about the future.",
    },
    # ---------- More books (P-1028 … P-1040) ----------
    {
        "product_id": "P-1028", "product_name": "How to Win Friends and Influence People", "author": "Dale Carnegie",
        "genre": "Self-development", "category": "Personal Development", "price": 4800, "stock": 17,
        "year": 1936, "pages": 288, "edition": "Paperback edition", "languages": ["English", "Russian", "Kazakh"],
        "description": "Dale Carnegie shares simple rules for talking to people, making a good impression and solving conflicts without arguments. One of the best-known books about communication.",
    },
    {
        "product_id": "P-1029", "product_name": "Winnie-the-Pooh", "author": "A. A. Milne",
        "genre": "Children's story", "category": "Children's Books", "price": 3400, "stock": 21,
        "year": 1926, "pages": 176, "edition": "Illustrated hardcover edition", "languages": ["English", "Russian"],
        "description": "A bear of very little brain, his friend Piglet and the other animals of the Hundred Acre Wood go looking for honey, hunt for Heffalumps and celebrate birthdays. Gentle stories for reading aloud.",
    },
    {
        "product_id": "P-1030", "product_name": "Pippi Longstocking", "author": "Astrid Lindgren",
        "genre": "Children's story", "category": "Children's Books", "price": 3600, "stock": 10,
        "year": 1945, "pages": 160, "edition": "Illustrated hardcover edition", "languages": ["English", "Russian"],
        "description": "Pippi is nine, lives alone with a horse and a monkey and is the strongest girl in the world. Her neighbours Tommy and Annika discover that life next to Pippi is never boring.",
    },
    {
        "product_id": "P-1031", "product_name": "The White Ship", "author": "Chingiz Aitmatov",
        "genre": "Novel", "category": "Literature", "price": 4100, "stock": 6,
        "year": 1970, "pages": 192, "edition": "Paperback edition", "languages": ["Russian", "Kazakh"],
        "description": "A lonely boy lives with his grandfather at a forest outpost in the mountains and believes in the legend of the Horned Mother Deer. He dreams of turning into a fish and swimming to the white ship where his father may be.",
    },
    {
        "product_id": "P-1032", "product_name": "Dune", "author": "Frank Herbert",
        "genre": "Science fiction", "category": "Fiction", "price": 7900, "stock": 12,
        "year": 1965, "pages": 688, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Young Paul Atreides moves with his family to the desert planet Arrakis, the only source of the most valuable substance in the universe. Betrayal forces him to survive among the desert people and discover his own destiny.",
    },
    {
        "product_id": "P-1033", "product_name": "Harry Potter and the Chamber of Secrets", "author": "J. K. Rowling",
        "genre": "Fantasy", "category": "Fantasy", "price": 7200, "stock": 9,
        "year": 1998, "pages": 352, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "In his second year at Hogwarts Harry hears a mysterious voice in the walls, and students are found turned to stone. Harry, Ron and Hermione try to find out who has opened the legendary Chamber of Secrets.",
    },
    {
        "product_id": "P-1034", "product_name": "The Great Gatsby", "author": "F. Scott Fitzgerald",
        "genre": "Classic novel", "category": "Classics", "price": 3900, "stock": 14,
        "year": 1925, "pages": 180, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Nick Carraway moves next door to the mysterious millionaire Jay Gatsby, famous for his huge parties. Behind the glamour of the 1920s lies a story of love, ambition and the American dream.",
    },
    {
        "product_id": "P-1035", "product_name": "War and Peace", "author": "Leo Tolstoy",
        "genre": "Classic novel", "category": "Classics", "price": 8900, "stock": 4,
        "year": 1869, "pages": 1296, "edition": "Paperback edition", "languages": ["Russian", "English"],
        "description": "Several noble families live through the Napoleonic wars in Russia. Battles, balls and quiet family scenes come together in a great novel about history, love and the meaning of life.",
    },
    {
        "product_id": "P-1036", "product_name": "And Then There Were None", "author": "Agatha Christie",
        "genre": "Detective", "category": "Mystery & Thriller", "price": 4300, "stock": 11,
        "year": 1939, "pages": 272, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Ten strangers are invited to a lonely island, and the host never arrives. One by one the guests begin to die, and they understand that the killer is one of them.",
    },
    {
        "product_id": "P-1037", "product_name": "The Selfish Gene", "author": "Richard Dawkins",
        "genre": "Popular science", "category": "Popular Science", "price": 6600, "stock": 7,
        "year": 1976, "pages": 360, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Richard Dawkins looks at evolution from the point of view of genes. The book explains how cooperation and even kindness between animals can come from natural selection.",
    },
    {
        "product_id": "P-1038", "product_name": "SPQR: A History of Ancient Rome", "author": "Mary Beard",
        "genre": "History", "category": "History", "price": 8200, "stock": 0,
        "year": 2015, "pages": 608, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Mary Beard tells how a small town on the Tiber became the centre of a huge empire. The book shows not only emperors and wars but also the everyday life of ordinary Romans.",
    },
    {
        "product_id": "P-1039", "product_name": "The Lean Startup", "author": "Eric Ries",
        "genre": "Business", "category": "Business", "price": 6300, "stock": 8,
        "year": 2011, "pages": 336, "edition": "Hardcover edition", "languages": ["English", "Russian"],
        "description": "Eric Ries explains how to build a startup step by step: make a simple product, test it with real customers and learn quickly from the results instead of guessing.",
    },
    {
        "product_id": "P-1040", "product_name": "The Intelligent Investor", "author": "Benjamin Graham",
        "genre": "Finance", "category": "Business", "price": 8500, "stock": 5,
        "year": 1949, "pages": 640, "edition": "Paperback edition", "languages": ["English", "Russian"],
        "description": "Benjamin Graham describes value investing: how to buy shares carefully, protect yourself from big losses and not follow the emotions of the market. A classic book about long-term investing.",
    },
]


def product_fields(book, category):
    """Fields for Product(...) built from one BOOKS entry."""
    return {
        "product_name": book["product_name"],
        "author": book["author"],
        "description": book["description"],
        "page_count": book["pages"],
        "edition_info": book["edition"],
        "available_languages": book["languages"],
        "publication_year": book["year"],
        "genre": book["genre"],
        "category": category,
        "price": book["price"],
        "stock_quantity": book["stock"],
    }
