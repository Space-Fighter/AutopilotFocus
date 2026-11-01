// Package verdict holds the POST /v1/verdict endpoint: the extension asks
// "should this page be blocked?" and gets allow or block back.
package verdict

// These structs mirror ai-service/src/ai_service/schemas.py. The `json:"..."` tags
// must match the Python field names exactly, or the data silently goes missing.

type YouTube struct {
	VideoID     string   `json:"video_id"`
	Channel     string   `json:"channel,omitempty"`
	Tags        []string `json:"tags,omitempty"`
	Category    string   `json:"category,omitempty"`
	Description string   `json:"description,omitempty"`
}

// Page is what the extension's content script extracts from the page.
type Page struct {
	URL             string   `json:"url"`
	Title           string   `json:"title,omitempty"`
	MetaDescription string   `json:"meta_description,omitempty"`
	Headings        []string `json:"headings,omitempty"`
	TextExcerpt     string   `json:"text_excerpt,omitempty"`
	YouTube         *YouTube `json:"youtube,omitempty"` // pointer: nil when the page isn't YouTube
}

// Goal is what the student typed when they turned blocking On.
type Goal struct {
	Text    string `json:"text"`
	Profile string `json:"profile,omitempty"`
}

// Request is the body of POST /v1/verdict (and also of Python's /v1/classify).
type Request struct {
	Page Page `json:"page"`
	Goal Goal `json:"goal"`
}

// Verdict is the answer, passed back from Python unchanged.
type Verdict struct {
	Decision   string   `json:"decision"` // "allow" or "block"
	Reason     string   `json:"reason"`
	Source     string   `json:"source"`               // "embedding", "llm" or "fallback"
	Similarity *float64 `json:"similarity,omitempty"` // pointer: Python sends null on fallback
}
