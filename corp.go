package main

import (
	"net/http"

	"github.com/gorilla/mux"
)

// Serves a pixel with the chosen CORP directive in the Cross-Origin-Resource-Policy header
func CorpHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)
	directive := mux.Vars(r)["directive"]

	switch directive {
	case "same-site", "same-origin", "cross-origin":
		w.Header().Set("Cross-Origin-Resource-Policy", directive)
	case "none":
		// Don't set header
	default:
		http.Error(w, "Invalid CORP directive", http.StatusBadRequest)
		return
	}

	http.ServeFile(w, r, "./static/pixel.png")
}
