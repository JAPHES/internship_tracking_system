(function () {
    "use strict";

    const storageKeys = {
        access: "its_access_token",
        refresh: "its_refresh_token",
        user: "its_current_user",
    };

    class ApiError extends Error {
        constructor(message, status, data) {
            super(message);
            this.name = "ApiError";
            this.status = status;
            this.data = data;
        }
    }

    function getStoredUser() {
        try {
            return JSON.parse(sessionStorage.getItem(storageKeys.user)) || null;
        } catch (_error) {
            return null;
        }
    }

    function saveSession(payload) {
        sessionStorage.setItem(storageKeys.access, payload.access);
        sessionStorage.setItem(storageKeys.refresh, payload.refresh);
        sessionStorage.setItem(storageKeys.user, JSON.stringify(payload.user));
        updateNavigation(payload.user);
    }

    function clearSession() {
        Object.values(storageKeys).forEach((key) => sessionStorage.removeItem(key));
        updateNavigation(null);
    }

    function messageFromPayload(data, fallback) {
        if (!data) return fallback;
        if (typeof data === "string") return data;
        if (data.error?.message) return data.error.message;
        if (data.detail) return Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
        const first = Object.values(data)[0];
        if (Array.isArray(first)) return first.join(" ");
        if (typeof first === "string") return first;
        return fallback;
    }

    async function parseResponse(response) {
        const contentType = response.headers.get("content-type") || "";
        if (response.status === 204) return null;
        if (contentType.includes("application/json")) return response.json();
        return response.text();
    }

    async function refreshAccessToken() {
        const refresh = sessionStorage.getItem(storageKeys.refresh);
        if (!refresh) return false;

        const response = await fetch("/api/v1/auth/token/refresh/", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({ refresh }),
        });
        if (!response.ok) {
            clearSession();
            return false;
        }
        const payload = await response.json();
        sessionStorage.setItem(storageKeys.access, payload.access);
        if (payload.refresh) sessionStorage.setItem(storageKeys.refresh, payload.refresh);
        return true;
    }

    async function request(url, options = {}, mayRefresh = true) {
        const headers = new Headers(options.headers || {});
        headers.set("Accept", "application/json");
        if (options.body && !(options.body instanceof FormData)) {
            headers.set("Content-Type", "application/json");
        }
        const access = sessionStorage.getItem(storageKeys.access);
        if (access && options.auth !== false) headers.set("Authorization", `Bearer ${access}`);

        const response = await fetch(url, { ...options, headers });
        if (response.status === 401 && mayRefresh && options.auth !== false) {
            const refreshed = await refreshAccessToken();
            if (refreshed) return request(url, options, false);
        }

        const data = await parseResponse(response);
        if (!response.ok) {
            const details = data?.error?.details || data;
            throw new ApiError(
                messageFromPayload(data, "The request could not be completed."),
                response.status,
                details,
            );
        }
        return data;
    }

    function updateNavigation(user = getStoredUser()) {
        document.querySelectorAll("[data-guest-only]").forEach((element) => {
            element.hidden = Boolean(user);
        });
        document.querySelectorAll("[data-logout], [data-user-chip]").forEach((element) => {
            element.hidden = !user;
        });
        if (!user) return;

        const name = user.full_name || user.email || "User";
        const initials = `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}` || "U";
        document.querySelectorAll("[data-user-name]").forEach((element) => { element.textContent = name; });
        document.querySelectorAll("[data-user-role]").forEach((element) => {
            element.textContent = String(user.role || "user").toLowerCase();
        });
        document.querySelectorAll("[data-user-initials]").forEach((element) => {
            element.textContent = initials.toUpperCase();
        });
    }

    function showToast(message, type = "success") {
        const region = document.querySelector("[data-toast-region]");
        if (!region) return;
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.setAttribute("role", type === "error" ? "alert" : "status");
        toast.textContent = message;
        region.appendChild(toast);
        window.setTimeout(() => toast.remove(), 4200);
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function formatDate(value) {
        if (!value) return "—";
        const date = new Date(`${value}T00:00:00`);
        if (Number.isNaN(date.getTime())) return value;
        return new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short", year: "numeric" }).format(date);
    }

    function listResults(payload) {
        return Array.isArray(payload) ? payload : (payload?.results || []);
    }

    document.addEventListener("DOMContentLoaded", () => {
        updateNavigation();

        const toggle = document.querySelector(".nav-toggle");
        const navigation = document.querySelector(".primary-nav");
        toggle?.addEventListener("click", () => {
            const open = navigation.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", String(open));
        });

        document.querySelectorAll("[data-logout]").forEach((button) => {
            button.addEventListener("click", () => {
                clearSession();
                showToast("You have been signed out.");
                window.location.assign("/login/");
            });
        });
    });

    window.ITS = {
        ApiError,
        clearSession,
        escapeHtml,
        formatDate,
        getStoredUser,
        listResults,
        request,
        saveSession,
        showToast,
    };
}());
