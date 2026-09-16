(function () {
    "use strict";

    function clearErrors(form) {
        form.querySelectorAll("[aria-invalid='true']").forEach((field) => field.removeAttribute("aria-invalid"));
        form.querySelectorAll("[data-error-for]").forEach((element) => { element.textContent = ""; });
        const alert = document.querySelector("[data-form-alert]");
        if (alert) {
            alert.hidden = true;
            alert.classList.remove("success");
            alert.textContent = "";
        }
    }

    function showFormErrors(form, error) {
        const data = error.data || {};
        let hasFieldError = false;
        Object.entries(data).forEach(([fieldName, messages]) => {
            const field = form.elements.namedItem(fieldName);
            const errorNode = form.querySelector(`[data-error-for="${fieldName}"]`);
            if (!field || !errorNode) return;
            const message = Array.isArray(messages) ? messages.join(" ") : String(messages);
            field.setAttribute("aria-invalid", "true");
            errorNode.textContent = message;
            hasFieldError = true;
        });
        if (!hasFieldError || data.detail) showAlert(error.message || "Please check the supplied information.");
    }

    function showAlert(message, success = false) {
        const alert = document.querySelector("[data-form-alert]");
        if (!alert) return;
        alert.textContent = message;
        alert.classList.toggle("success", success);
        alert.hidden = false;
        alert.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function setSubmitting(button, isSubmitting, label) {
        if (!button) return;
        if (!button.dataset.originalLabel) button.dataset.originalLabel = button.innerHTML;
        button.disabled = isSubmitting;
        button.innerHTML = isSubmitting ? label : button.dataset.originalLabel;
    }

    async function signIn(email, password) {
        const payload = await window.ITS.request("/api/v1/auth/token/", {
            method: "POST",
            auth: false,
            body: JSON.stringify({ email, password }),
        });
        window.ITS.saveSession(payload);
        return payload;
    }

    function initialisePasswordToggles() {
        document.querySelectorAll("[data-toggle-password]").forEach((button) => {
            button.addEventListener("click", () => {
                const input = document.getElementById(button.dataset.togglePassword);
                const show = input.type === "password";
                input.type = show ? "text" : "password";
                button.textContent = show ? "Hide" : "Show";
                button.setAttribute("aria-label", `${show ? "Hide" : "Show"} password`);
            });
        });
    }

    function initialiseLogin() {
        const form = document.getElementById("login-form");
        if (!form) return;
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            clearErrors(form);
            const button = form.querySelector("[data-submit-button]");
            setSubmitting(button, true, "Signing in…");
            try {
                await signIn(form.email.value.trim(), form.password.value);
                window.location.assign("/dashboard/");
            } catch (error) {
                showFormErrors(form, error);
                setSubmitting(button, false);
            }
        });
    }

    function initialiseRegistration() {
        const form = document.getElementById("registration-form");
        if (!form) return;
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            clearErrors(form);
            const button = form.querySelector("[data-submit-button]");
            if (form.password.value !== form.password_confirm.value) {
                form.password_confirm.setAttribute("aria-invalid", "true");
                form.querySelector("[data-error-for='password_confirm']").textContent = "Passwords do not match.";
                return;
            }
            setSubmitting(button, true, "Creating account…");
            const payload = {
                email: form.email.value.trim(),
                password: form.password.value,
                first_name: form.first_name.value.trim(),
                last_name: form.last_name.value.trim(),
                registration_number: form.registration_number.value.trim(),
                programme: form.programme.value.trim(),
                department: form.department.value.trim(),
                phone_number: form.phone_number.value.trim(),
            };
            try {
                await window.ITS.request("/api/v1/auth/register/student/", {
                    method: "POST",
                    auth: false,
                    body: JSON.stringify(payload),
                });
                showAlert("Account created. Opening your dashboard…", true);
                await signIn(payload.email, payload.password);
                window.setTimeout(() => window.location.assign("/dashboard/"), 500);
            } catch (error) {
                showFormErrors(form, error);
                setSubmitting(button, false);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        initialisePasswordToggles();
        initialiseLogin();
        initialiseRegistration();
    });
}());
