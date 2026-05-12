package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/gorilla/mux"
)

const CSP_COOKIE_NAME = "cspCookie"

const HTTPONLY_COOKIE_NAME = "httpOnlyCookie"
const HTTPONLY_COOKIE_SETVAL = "619"

const REQUEST_SECURE_COOKIE_NAME = "requestSecureCookie"
const REQUEST_SECURE_COOKIE_SETVAL = "881"

const SESSION_SECURE_COOKIE_NAME = "sessionSecureCookie"
const SESSION_SECURE_COOKIE_SETVAL = "415"

func ClearCookiesHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	path := regexp.MustCompile("(.*/).*?$").ReplaceAllString(r.URL.Path, "$1")
	expires := time.Now().Add(-240 * time.Hour)

	for _, c := range r.Cookies() {
		// Don't destroy the cookie containing the session ID (set by /test)
		if c.Name != SESSION_ID_COOKIE_NAME {
			c.Value = "."
			c.Domain = RequestHost(r)
			c.Path = path
			c.Expires = expires

			http.SetCookie(w, c)
		}
	}

	http.ServeFile(w, r, "./static/pixel.png")
}

func CSPCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	cookieDomain := ""
	if regexp.MustCompile("^browseraudit\\.(com|org)$").MatchString(RequestHost(r)) {
		cookieDomain = "." + RequestHost(r)
	} else {
		cookieDomain = RequestHost(r)
	}
	escapedDomain := regexp.MustCompile("\\.").ReplaceAllString(RequestHost(r), "_")

	expires := time.Now().Add(5 * time.Minute)
	cookie := &http.Cookie{Name: CSP_COOKIE_NAME + "_" + escapedDomain,
		Value:   RequestHost(r),
		Domain:  cookieDomain,
		Path:    "/",
		Expires: expires}
	http.SetCookie(w, cookie)

	http.ServeFile(w, r, "./static/pixel.png")
}

func HttpOnlyCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	expires := time.Now().Add(5 * time.Minute)
	cookie := &http.Cookie{Name: HTTPONLY_COOKIE_NAME,
		Value:    HTTPONLY_COOKIE_SETVAL,
		Domain:   ".browseraudit.com",
		Path:     "/",
		Expires:  expires,
		HttpOnly: true}
	http.SetCookie(w, cookie)
}

func SetRequestSecureCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	expires := time.Now().Add(5 * time.Minute)
	cookie := &http.Cookie{Name: REQUEST_SECURE_COOKIE_NAME,
		Value:   REQUEST_SECURE_COOKIE_SETVAL,
		Domain:  ".browseraudit.com",
		Path:    "/",
		Expires: expires,
		Secure:  true}
	http.SetCookie(w, cookie)

	http.ServeFile(w, r, "./static/pixel.png")
}

func GetRequestSecureCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	c, err := r.Cookie(REQUEST_SECURE_COOKIE_NAME)
	if err == nil {
		template.HTMLEscape(w, []byte(c.Value))
	} else {
		fmt.Fprintf(w, "nil")
	}
}

func SetSessionSecureCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	session := store.Get(w, r)
	c, err := r.Cookie(SESSION_SECURE_COOKIE_NAME)
	if err != nil || r.Header.Get("X-Forwarded-Proto") == "https" {
		session.Set(SESSION_SECURE_COOKIE_NAME, "nil")
	} else {
		session.Set(SESSION_SECURE_COOKIE_NAME, c.Value)
	}

	http.ServeFile(w, r, "./static/pixel.png")
}

func GetSessionSecureCookieHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	session := store.Get(w, r)

	c, err := session.Get(SESSION_SECURE_COOKIE_NAME)
	if err != nil {
		log.Println("nil session secure cookie")
		c = "nil"
	}

	template.HTMLEscape(w, []byte(c))
}

func GetDestroyMeHandler(w http.ResponseWriter, r *http.Request) {
	DontCache(&w)

	c, err := r.Cookie("destroyMe")
	if err == nil {
		template.HTMLEscape(w, []byte(c.Value))
	} else {
		fmt.Fprintf(w, "nil")
	}
}

// Sets a cookie with a given SameSite policy
func SetRequestSameSiteCookieHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["name"]
	policy := vars["policy"]
	var sameSite http.SameSite

	secure := true
	switch strings.ToLower(policy) {
	case "none":
		sameSite = http.SameSiteNoneMode
	case "lax":
		sameSite = http.SameSiteLaxMode
	case "strict":
		sameSite = http.SameSiteStrictMode
	case "none-insecure":
		sameSite = http.SameSiteNoneMode
		secure = false
	default:
		http.Error(w, "invalid policy", http.StatusBadRequest)
		return
	}

	cookie := &http.Cookie{
		Name:  name,
		Value: "test-value",
		// Needs to be .browseraudit.org for SameSite since the cookie is being sent from .com -> .org,
		// so Domain check isn't a problem and we can test SameSite | also set the cookie from .org so RequestHost(r) returns .org domain
		Domain:   "." + RequestHost(r),
		Path:     "/",
		Expires:  time.Now().Add(1 * time.Minute),
		SameSite: sameSite,
		Secure:   secure,
	}
	http.SetCookie(w, cookie)
	http.ServeFile(w, r, "./static/pixel.png")
}

// Saves whether the cookie arrived in this request (called cross-site)
func SetSessionSameSiteCookieHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["name"]
	session := store.Get(w, r)
	c, err := r.Cookie(name)
	if err == nil {
		session.Set(name, c.Value)
	} else {
		session.Set(name, "none")
	}
	http.ServeFile(w, r, "./static/pixel.png")
}

// Returns the saved value to the JS test
func GetSessionSameSiteCookieHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	session := store.Get(w, r)
	val, err := session.Get(vars["name"])
	if err != nil {
		val = "none"
	}
	template.HTMLEscape(w, []byte(val))
}
