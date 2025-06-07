#!/usr/bin/env python3
# NebulaFusion Browser - URL Utilities

import os
import sys
import re
import urllib.parse
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

class UrlUtils(QObject):
    """
    URL utility functions for NebulaFusion browser.
    Provides URL parsing, validation, and manipulation.
    """
    
    # Signals
    url_validated = pyqtSignal(str, bool)  # url, is_valid
    
    def __init__(self):
        """Initialize the URL utilities."""
        super().__init__()
        
        # Common TLDs for validation
        self.common_tlds = [
            "com", "org", "net", "edu", "gov", "mil", "io", "co", "info", "biz",
            "me", "tv", "app", "dev", "ai", "uk", "us", "ca", "au", "de", "fr",
            "jp", "cn", "ru", "br", "in", "it", "nl", "es", "se", "no", "fi",
            "dk", "ch", "at", "be", "ie", "nz", "sg", "ae", "sa", "za", "mx",
            "ar", "cl", "pe", "co", "ve", "ec", "bo", "py", "uy", "cr", "pa",
            "do", "hn", "sv", "ni", "gt", "cu", "pr", "jm", "bs", "bb", "tt",
            "lc", "vc", "gd", "ag", "dm", "kn", "tc", "vg", "ai", "ms", "ky",
            "bm", "gl", "pm", "fo", "is", "li", "lu", "mc", "sm", "va", "ad",
            "gi", "je", "gg", "im", "mt", "cy", "gr", "tr", "il", "lb", "jo",
            "kw", "qa", "bh", "om", "ye", "ir", "iq", "sy", "eg", "ly", "tn",
            "dz", "ma", "mr", "ml", "sn", "gm", "gw", "gn", "sl", "lr", "ci",
            "gh", "tg", "bj", "ne", "ng", "cm", "td", "cf", "ga", "cg", "cd",
            "ao", "na", "bw", "zw", "mz", "zm", "mw", "tz", "ke", "ug", "rw",
            "bi", "et", "dj", "so", "er", "sd", "ss", "mg", "mu", "re", "sc",
            "mv", "lk", "bd", "np", "bt", "mm", "th", "la", "kh", "vn", "my",
            "ph", "id", "tl", "bn", "pw", "fm", "mh", "nr", "sb", "vu", "fj",
            "to", "ws", "ck", "nu", "tv", "ki", "pf", "nc", "wf", "as", "gu",
            "mp", "pg", "nf", "cx", "cc", "hm", "tk", "travel", "museum", "jobs",
            "mobi", "tel", "asia", "coop", "cat", "pro", "int", "aero", "post",
            "xyz", "top", "club", "site", "online", "shop", "blog", "tech", "store",
            "cloud", "space", "live", "life", "world", "today", "digital", "network",
            "design", "game", "games", "media", "news", "video", "music", "art",
            "health", "care", "doctor", "hospital", "school", "academy", "university",
            "college", "education", "institute", "center", "foundation", "church",
            "community", "social", "group", "team", "company", "business", "agency",
            "studio", "works", "creative", "solutions", "consulting", "partners",
            "limited", "ltd", "inc", "llc", "corp", "gmbh", "legal", "law", "attorney",
            "lawyer", "accountant", "tax", "finance", "financial", "bank", "money",
            "insurance", "invest", "investment", "fund", "capital", "holdings",
            "property", "properties", "realty", "estate", "construction", "build",
            "builder", "building", "house", "home", "homes", "land", "farm", "garden",
            "food", "restaurant", "cafe", "coffee", "bar", "pub", "beer", "wine",
            "pizza", "sushi", "kitchen", "cook", "cooking", "chef", "recipe", "recipes",
            "diet", "fitness", "gym", "yoga", "run", "running", "bike", "biking",
            "swim", "swimming", "golf", "tennis", "soccer", "football", "baseball",
            "basketball", "hockey", "sport", "sports", "fan", "fans", "team", "league",
            "racing", "car", "cars", "auto", "automotive", "vehicle", "vehicles",
            "motorcycle", "motorcycles", "boat", "boats", "yacht", "yachts", "plane",
            "planes", "jet", "jets", "airline", "airlines", "flight", "flights",
            "travel", "traveling", "traveler", "vacation", "vacations", "holiday",
            "holidays", "tour", "tours", "tourism", "tourist", "cruise", "cruises",
            "resort", "resorts", "hotel", "hotels", "motel", "motels", "hostel",
            "hostels", "camping", "camp", "beach", "mountain", "mountains", "lake",
            "lakes", "river", "rivers", "ocean", "sea", "island", "islands", "park",
            "parks", "forest", "nature", "wildlife", "animal", "animals", "pet",
            "pets", "dog", "dogs", "cat", "cats", "bird", "birds", "fish", "horse",
            "horses", "farm", "farming", "garden", "gardening", "plant", "plants",
            "flower", "flowers", "tree", "trees", "photography", "photo", "photos",
            "picture", "pictures", "image", "images", "camera", "video", "videos",
            "film", "films", "movie", "movies", "cinema", "theater", "theatre",
            "concert", "concerts", "festival", "festivals", "event", "events",
            "wedding", "weddings", "party", "parties", "dance", "dancing", "music",
            "band", "bands", "singer", "singers", "song", "songs", "album", "albums",
            "artist", "artists", "art", "arts", "gallery", "galleries", "museum",
            "museums", "exhibition", "exhibitions", "fashion", "style", "design",
            "designer", "designers", "model", "models", "beauty", "makeup", "hair",
            "salon", "spa", "massage", "nail", "nails", "tattoo", "tattoos", "jewelry",
            "jewellery", "watch", "watches", "clothing", "clothes", "fashion", "shoe",
            "shoes", "handbag", "handbags", "accessory", "accessories", "furniture",
            "furnishings", "decor", "decoration", "decorations", "interior", "exteriors",
            "architecture", "architect", "architects", "engineering", "engineer",
            "engineers", "science", "scientist", "scientists", "research", "lab",
            "laboratory", "laboratories", "technology", "technologies", "tech",
            "computer", "computers", "software", "hardware", "program", "programming",
            "code", "coding", "developer", "developers", "web", "website", "websites",
            "host", "hosting", "server", "servers", "cloud", "data", "database",
            "storage", "backup", "security", "secure", "protection", "privacy",
            "private", "vpn", "network", "networks", "internet", "online", "digital",
            "virtual", "mobile", "phone", "phones", "smartphone", "smartphones",
            "tablet", "tablets", "laptop", "laptops", "desktop", "desktops", "device",
            "devices", "gadget", "gadgets", "electronic", "electronics", "electric",
            "electrical", "power", "energy", "solar", "wind", "water", "gas", "oil",
            "fuel", "green", "eco", "environment", "environmental", "sustainable",
            "sustainability", "recycle", "recycling", "organic", "natural", "bio",
            "health", "healthy", "wellness", "medical", "medicine", "doctor", "doctors",
            "dentist", "dentists", "dental", "hospital", "hospitals", "clinic",
            "clinics", "pharmacy", "pharmacies", "drug", "drugs", "vitamin", "vitamins",
            "supplement", "supplements", "therapy", "therapist", "therapists",
            "counseling", "counselor", "counselors", "psychology", "psychologist",
            "psychologists", "psychiatry", "psychiatrist", "psychiatrists", "mental",
            "education", "educational", "learn", "learning", "teach", "teaching",
            "teacher", "teachers", "student", "students", "school", "schools",
            "university", "universities", "college", "colleges", "academy", "academies",
            "institute", "institutes", "course", "courses", "class", "classes",
            "training", "coach", "coaching", "tutor", "tutoring", "tutors", "career",
            "careers", "job", "jobs", "employment", "employer", "employers", "hire",
            "hiring", "recruit", "recruiting", "recruitment", "resume", "resumes",
            "interview", "interviews", "work", "working", "worker", "workers",
            "business", "businesses", "company", "companies", "startup", "startups",
            "entrepreneur", "entrepreneurs", "enterprise", "enterprises", "corporate",
            "corporation", "corporations", "industry", "industries", "industrial",
            "manufacture", "manufacturing", "manufacturer", "manufacturers", "product",
            "products", "service", "services", "solution", "solutions", "consulting",
            "consultant", "consultants", "advisor", "advisors", "expert", "experts",
            "professional", "professionals", "specialist", "specialists", "broker",
            "brokers", "agent", "agents", "agency", "agencies", "firm", "firms",
            "partner", "partners", "partnership", "partnerships", "association",
            "associations", "foundation", "foundations", "organization", "organizations",
            "charity", "charities", "nonprofit", "community", "communities", "society",
            "club", "clubs", "group", "groups", "team", "teams", "member", "members",
            "membership", "forum", "forums", "board", "boards", "committee", "committees",
            "council", "councils", "government", "governments", "political", "politics",
            "policy", "policies", "law", "laws", "legal", "lawyer", "lawyers", "attorney",
            "attorneys", "court", "courts", "justice", "judge", "judges", "police",
            "military", "army", "navy", "air", "force", "defense", "security", "guard",
            "guards", "protection", "emergency", "fire", "firefighter", "firefighters",
            "rescue", "safety", "safe", "insurance", "insure", "insurer", "insurers",
            "bank", "banks", "banking", "financial", "finance", "money", "cash",
            "credit", "loan", "loans", "mortgage", "mortgages", "invest", "investing",
            "investment", "investments", "investor", "investors", "fund", "funds",
            "funding", "capital", "wealth", "tax", "taxes", "taxation", "accounting",
            "accountant", "accountants", "budget", "budgeting", "save", "saving",
            "savings", "retire", "retirement", "pension", "estate", "will", "trust",
            "property", "properties", "real", "estate", "land", "housing", "house",
            "houses", "home", "homes", "apartment", "apartments", "condo", "condos",
            "rent", "rental", "rentals", "lease", "leasing", "buy", "buying", "sell",
            "selling", "sale", "sales", "auction", "auctions", "bid", "bidding",
            "market", "marketing", "advertise", "advertising", "advertisement",
            "advertisements", "promote", "promotion", "promotions", "brand", "branding",
            "brands", "logo", "logos", "identity", "campaign", "campaigns", "media",
            "press", "news", "newspaper", "newspapers", "magazine", "magazines",
            "journal", "journals", "blog", "blogs", "blogger", "bloggers", "article",
            "articles", "story", "stories", "book", "books", "ebook", "ebooks",
            "publish", "publishing", "publisher", "publishers", "author", "authors",
            "write", "writing", "writer", "writers", "content", "copy", "copyright",
            "trademark", "trademarks", "patent", "patents", "intellectual", "property",
            "creative", "creation", "create", "creator", "creators", "make", "maker",
            "makers", "craft", "crafts", "art", "artist", "artists", "design", "designer",
            "designers", "style", "fashion", "shop", "shopping", "store", "stores",
            "mall", "outlet", "outlets", "market", "marketplace", "buy", "buyer",
            "buyers", "sell", "seller", "sellers", "vendor", "vendors", "supply",
            "supplier", "suppliers", "wholesale", "retail", "deal", "deals", "discount",
            "discounts", "coupon", "coupons", "save", "savings", "free", "cheap",
            "price", "prices", "cost", "costs", "value", "quality", "review", "reviews",
            "rate", "rating", "ratings", "compare", "comparison", "best", "top",
            "popular", "trend", "trends", "trending", "hot", "new", "latest", "modern",
            "contemporary", "classic", "vintage", "antique", "retro", "custom",
            "personalize", "personalized", "unique", "original", "authentic", "genuine",
            "official", "authorized", "premium", "luxury", "exclusive", "elite",
            "vip", "pro", "professional", "expert", "master", "guru", "genius",
            "wizard", "ninja", "hero", "champion", "winner", "success", "successful",
            "achieve", "achievement", "goal", "goals", "dream", "dreams", "inspire",
            "inspiration", "motivate", "motivation", "positive", "happy", "happiness",
            "joy", "fun", "enjoy", "love", "life", "live", "living", "lifestyle",
            "experience", "adventure", "explore", "discovery", "discover", "find",
            "search", "seek", "guide", "guides", "help", "support", "assist", "service",
            "care", "trust", "reliable", "dependable", "honest", "integrity", "ethical",
            "moral", "fair", "just", "right", "good", "better", "best", "perfect",
            "excellent", "outstanding", "superior", "supreme", "ultimate", "extreme",
            "mega", "super", "hyper", "ultra", "maximum", "minimum", "medium", "average",
            "standard", "basic", "simple", "easy", "quick", "fast", "rapid", "swift",
            "instant", "immediate", "now", "today", "daily", "weekly", "monthly",
            "yearly", "annual", "season", "seasonal", "summer", "winter", "spring",
            "fall", "autumn", "holiday", "christmas", "halloween", "easter", "birthday",
            "anniversary", "wedding", "baby", "family", "friend", "friends", "partner",
            "partners", "relationship", "relationships", "date", "dating", "match",
            "matching", "meet", "meeting", "connect", "connection", "connections",
            "network", "networking", "social", "society", "community", "local",
            "global", "international", "world", "worldwide", "universal", "earth",
            "planet", "space", "universe", "galaxy", "star", "stars", "sun", "moon",
            "sky", "heaven", "paradise", "dream", "fantasy", "magic", "magical",
            "mystic", "mystical", "spiritual", "spirit", "soul", "mind", "body",
            "heart", "life", "death", "god", "goddess", "angel", "demon", "devil",
            "evil", "good", "light", "dark", "black", "white", "red", "blue", "green",
            "yellow", "orange", "purple", "pink", "brown", "gray", "silver", "gold",
            "color", "colors", "colour", "colours", "rainbow", "nature", "natural",
            "earth", "water", "fire", "air", "wind", "storm", "rain", "snow", "ice",
            "cloud", "clouds", "sky", "sun", "moon", "star", "stars", "day", "night",
            "morning", "evening", "afternoon", "noon", "midnight", "time", "hour",
            "minute", "second", "moment", "instant", "now", "today", "tomorrow",
            "yesterday", "week", "month", "year", "decade", "century", "millennium",
            "age", "era", "period", "history", "future", "past", "present", "eternal",
            "forever", "always", "never", "sometimes", "often", "rarely", "seldom",
            "occasionally", "frequently", "regularly", "constantly", "continuously",
            "intermittently", "periodically", "sporadically", "randomly", "suddenly",
            "gradually", "slowly", "quickly", "rapidly", "swiftly", "hastily",
            "leisurely", "carefully", "cautiously", "recklessly", "boldly", "bravely",
            "fearlessly", "timidly", "shyly", "confidently", "proudly", "humbly",
            "modestly", "honestly", "sincerely", "truly", "really", "actually",
            "literally", "virtually", "practically", "essentially", "basically",
            "fundamentally", "primarily", "mainly", "mostly", "largely", "generally",
            "usually", "typically", "commonly", "normally", "naturally", "obviously",
            "clearly", "evidently", "apparently", "seemingly", "presumably", "supposedly",
            "allegedly", "reputedly", "reportedly", "arguably", "conceivably",
            "possibly", "probably", "likely", "unlikely", "certainly", "definitely",
            "absolutely", "undoubtedly", "unquestionably", "indisputably", "undeniably",
            "irrefutably", "incontrovertibly", "incontestably", "indubitably"
        ]
    
    def is_valid_url(self, url):
        """Check if a URL is valid."""
        # Check if URL is empty
        if not url:
            self.url_validated.emit(url, False)
            return False
        
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Check if URL has a scheme
        if "://" in url:
            # Parse URL
            parsed_url = urllib.parse.urlparse(url)
            
            # Check if scheme is valid
            if parsed_url.scheme not in ["http", "https", "file", "ftp", "ftps"]:
                self.url_validated.emit(url, False)
                return False
            
            # Check if netloc is valid
            if not parsed_url.netloc:
                self.url_validated.emit(url, False)
                return False
            
            self.url_validated.emit(url, True)
            return True
        else:
            # Check if URL is a valid domain
            if self._is_valid_domain(url):
                self.url_validated.emit(url, True)
                return True
            
            # Check if URL is a valid IP address
            if self._is_valid_ip(url):
                self.url_validated.emit(url, True)
                return True
            
            # Check if URL is a valid local file path
            if self._is_valid_file_path(url):
                self.url_validated.emit(url, True)
                return True
            
            # URL is not valid
            self.url_validated.emit(url, False)
            return False
    
    def _is_valid_domain(self, domain):
        """Check if a domain is valid."""
        # Remove any path or query
        domain = domain.split("/")[0].split("?")[0]
        
        # Check if domain has at least one dot
        if "." not in domain:
            return False
        
        # Check if domain has a valid TLD
        parts = domain.split(".")
        tld = parts[-1].lower()
        
        # Check if TLD is in common TLDs
        if tld not in self.common_tlds:
            return False
        
        # Check if domain name is valid
        domain_name = ".".join(parts[:-1])
        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$", domain_name):
            return False
        
        return True
    
    def _is_valid_ip(self, ip):
        """Check if an IP address is valid."""
        # Check if IP is IPv4
        if re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip):
            # Check if each octet is valid
            octets = ip.split(".")
            for octet in octets:
                if int(octet) > 255:
                    return False
            return True
        
        # Check if IP is IPv6
        if re.match(r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$", ip):
            return True
        
        return False
    
    def _is_valid_file_path(self, path):
        """Check if a file path is valid."""
        # Check if path is a valid file path
        if os.path.exists(path):
            return True
        
        return False
    
    def normalize_url(self, url):
        """Normalize a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Check if URL has a scheme
        if "://" not in url:
            # Check if URL is a valid domain
            if self._is_valid_domain(url):
                url = "https://" + url
            # Check if URL is a valid IP address
            elif self._is_valid_ip(url):
                url = "http://" + url
            # Check if URL is a valid local file path
            elif self._is_valid_file_path(url):
                url = "file://" + url
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Normalize scheme
        scheme = parsed_url.scheme.lower()
        
        # Normalize netloc
        netloc = parsed_url.netloc.lower()
        
        # Normalize path
        path = parsed_url.path
        if not path:
            path = "/"
        
        # Normalize query
        query = parsed_url.query
        
        # Normalize fragment
        fragment = parsed_url.fragment
        
        # Build normalized URL
        normalized_url = urllib.parse.urlunparse((scheme, netloc, path, "", query, fragment))
        
        return normalized_url
    
    def get_domain(self, url):
        """Get the domain from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get domain
        domain = parsed_url.netloc
        
        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]
        
        return domain
    
    def get_base_url(self, url):
        """Get the base URL (scheme + domain) from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get base URL
        base_url = parsed_url.scheme + "://" + parsed_url.netloc
        
        return base_url
    
    def get_path(self, url):
        """Get the path from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get path
        path = parsed_url.path
        
        return path
    
    def get_query(self, url):
        """Get the query from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get query
        query = parsed_url.query
        
        return query
    
    def get_query_params(self, url):
        """Get the query parameters from a URL as a dictionary."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get query parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Convert lists to single values if only one value
        for key, value in query_params.items():
            if len(value) == 1:
                query_params[key] = value[0]
        
        return query_params
    
    def get_fragment(self, url):
        """Get the fragment from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get fragment
        fragment = parsed_url.fragment
        
        return fragment
    
    def build_url(self, base_url, path="", query_params=None, fragment=""):
        """Build a URL from components."""
        # Check if base URL is already a QUrl
        if isinstance(base_url, QUrl):
            base_url = base_url.toString()
        
        # Parse base URL
        parsed_url = urllib.parse.urlparse(base_url)
        
        # Get scheme and netloc
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        
        # Normalize path
        if path and not path.startswith("/"):
            path = "/" + path
        
        # Build query string
        query = ""
        if query_params:
            query = urllib.parse.urlencode(query_params)
        
        # Build URL
        url = urllib.parse.urlunparse((scheme, netloc, path, "", query, fragment))
        
        return url
    
    def join_url(self, base_url, relative_url):
        """Join a base URL and a relative URL."""
        # Check if base URL is already a QUrl
        if isinstance(base_url, QUrl):
            base_url = base_url.toString()
        
        # Check if relative URL is already a QUrl
        if isinstance(relative_url, QUrl):
            relative_url = relative_url.toString()
        
        # Join URLs
        joined_url = urllib.parse.urljoin(base_url, relative_url)
        
        return joined_url
    
    def encode_url(self, url):
        """Encode a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Encode path
        path = urllib.parse.quote(parsed_url.path)
        
        # Encode query
        query = parsed_url.query
        
        # Encode fragment
        fragment = urllib.parse.quote(parsed_url.fragment)
        
        # Build encoded URL
        encoded_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, path, "", query, fragment))
        
        return encoded_url
    
    def decode_url(self, url):
        """Decode a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Decode path
        path = urllib.parse.unquote(parsed_url.path)
        
        # Decode query
        query = parsed_url.query
        
        # Decode fragment
        fragment = urllib.parse.unquote(parsed_url.fragment)
        
        # Build decoded URL
        decoded_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, path, "", query, fragment))
        
        return decoded_url
    
    def is_same_domain(self, url1, url2):
        """Check if two URLs have the same domain."""
        # Get domains
        domain1 = self.get_domain(url1)
        domain2 = self.get_domain(url2)
        
        # Compare domains
        return domain1 == domain2
    
    def is_subdomain(self, url, domain):
        """Check if a URL is a subdomain of a domain."""
        # Get URL domain
        url_domain = self.get_domain(url)
        
        # Check if URL domain is a subdomain of domain
        return url_domain.endswith("." + domain) or url_domain == domain
    
    def is_secure(self, url):
        """Check if a URL uses HTTPS."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Check if scheme is HTTPS
        return parsed_url.scheme.lower() == "https"
    
    def to_qurl(self, url):
        """Convert a URL string to a QUrl object."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            return url
        
        # Convert to QUrl
        return QUrl(url)
    
    def from_qurl(self, qurl):
        """Convert a QUrl object to a URL string."""
        # Check if URL is already a string
        if isinstance(qurl, str):
            return qurl
        
        # Convert to string
        return qurl.toString()
    
    def get_file_name_from_url(self, url):
        """Get the file name from a URL."""
        # Check if URL is already a QUrl
        if isinstance(url, QUrl):
            url = url.toString()
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Get path
        path = parsed_url.path
        
        # Get file name
        file_name = os.path.basename(path)
        
        # Remove query string and fragment
        file_name = file_name.split("?")[0].split("#")[0]
        
        return file_name
    
    def get_file_extension_from_url(self, url):
        """Get the file extension from a URL."""
        # Get file name
        file_name = self.get_file_name_from_url(url)
        
        # Get file extension
        _, file_extension = os.path.splitext(file_name)
        
        return file_extension
    
    def is_downloadable(self, url):
        """Check if a URL is likely to be a downloadable file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in downloadable extensions
        downloadable_extensions = [
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
            ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".txt", ".csv", ".json", ".xml", ".html", ".htm",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
            ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
            ".iso", ".img", ".bin", ".cue",
            ".apk", ".ipa", ".xpi", ".crx",
            ".ttf", ".otf", ".woff", ".woff2",
            ".py", ".js", ".css", ".php", ".java", ".c", ".cpp", ".h", ".cs", ".rb", ".go", ".rs", ".swift",
            ".sh", ".bat", ".ps1", ".vbs", ".pl", ".lua"
        ]
        
        return file_extension in downloadable_extensions
    
    def is_media(self, url):
        """Check if a URL is likely to be a media file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in media extensions
        media_extensions = [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
            ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"
        ]
        
        return file_extension in media_extensions
    
    def is_image(self, url):
        """Check if a URL is likely to be an image file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in image extensions
        image_extensions = [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif"
        ]
        
        return file_extension in image_extensions
    
    def is_video(self, url):
        """Check if a URL is likely to be a video file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in video extensions
        video_extensions = [
            ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".3g2"
        ]
        
        return file_extension in video_extensions
    
    def is_audio(self, url):
        """Check if a URL is likely to be an audio file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in audio extensions
        audio_extensions = [
            ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".mid", ".midi", ".opus"
        ]
        
        return file_extension in audio_extensions
    
    def is_document(self, url):
        """Check if a URL is likely to be a document file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in document extensions
        document_extensions = [
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".txt", ".csv", ".json", ".xml", ".html", ".htm", ".md", ".rtf", ".odt", ".ods", ".odp"
        ]
        
        return file_extension in document_extensions
    
    def is_archive(self, url):
        """Check if a URL is likely to be an archive file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in archive extensions
        archive_extensions = [
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz2", ".txz"
        ]
        
        return file_extension in archive_extensions
    
    def is_executable(self, url):
        """Check if a URL is likely to be an executable file."""
        # Get file extension
        file_extension = self.get_file_extension_from_url(url).lower()
        
        # Check if file extension is in executable extensions
        executable_extensions = [
            ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app", ".bat", ".sh", ".com", ".cmd", ".vbs", ".ps1"
        ]
        
        return file_extension in executable_extensions
