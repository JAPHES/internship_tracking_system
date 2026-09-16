(function () {
    "use strict";

    const { escapeHtml, formatDate, listResults, request } = window.ITS;

    const selectors = {
        loading: document.querySelector("[data-dashboard-loading]"),
        content: document.querySelector("[data-dashboard-content]"),
        error: document.querySelector("[data-dashboard-error]"),
        errorMessage: document.querySelector("[data-dashboard-error-message]"),
        metrics: document.querySelector("[data-metrics]"),
    };

    function greeting() {
        const hour = new Date().getHours();
        if (hour < 12) return "Good morning";
        if (hour < 18) return "Good afternoon";
        return "Good evening";
    }

    function metric(label, value, note, color = "var(--green)") {
        return `<article class="metric-card" style="--metric-color:${color}">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
            <small>${escapeHtml(note)}</small>
        </article>`;
    }

    function status(value) {
        const normalised = String(value || "unknown").toLowerCase();
        return `<span class="table-status is-${escapeHtml(normalised)}">${escapeHtml(normalised)}</span>`;
    }

    function emptyState(message) {
        return `<div class="empty-state">${escapeHtml(message)}</div>`;
    }

    function renderStudent(data, reportsPayload) {
        selectors.metrics.innerHTML = [
            metric("Expected reports", data.total_expected_reports, "Across the full placement"),
            metric("Submitted", data.total_submitted_reports, "Submitted or reviewed", "var(--blue)"),
            metric("Reviewed", data.total_reviewed_reports, "With supervisor feedback", "var(--green)"),
            metric("Overdue weeks", data.overdue_weeks?.length || 0, "Past weeks still missing", "var(--orange)"),
        ].join("");

        const view = document.querySelector("[data-student-view]");
        view.hidden = false;
        const placement = data.current_placement;
        const badge = document.querySelector("[data-placement-status]");
        const details = document.querySelector("[data-placement-details]");
        if (placement) {
            badge.textContent = placement.status.toLowerCase();
            badge.className = `status-badge is-${placement.status.toLowerCase()}`;
            details.innerHTML = `<div class="placement-summary">
                <div><small>Internship track</small><strong>${escapeHtml(placement.track_name)}</strong></div>
                <div><small>Supervisor</small><strong>${escapeHtml(placement.supervisor_name)}</strong></div>
                <div><small>Cohort</small><strong>${escapeHtml(placement.cohort_name)}</strong></div>
                <div><small>Duration</small><strong>${formatDate(placement.start_date)} — ${formatDate(placement.end_date)}</strong></div>
            </div>`;
        } else {
            details.innerHTML = emptyState("No placement has been assigned yet. Your administrator will create it.");
        }

        const percentage = Number(data.placement_progress_percentage || 0);
        document.querySelector("[data-large-progress]").innerHTML = `<div class="large-progress-ring" style="--progress:${Math.min(100, Math.max(0, percentage))}"><div><strong>${percentage}%</strong><small>complete</small></div></div><p class="progress-caption">Progress is calculated from the placement date range.</p>`;
        document.querySelector("[data-latest-feedback]").textContent = data.latest_supervisor_feedback || "No reviewed feedback is available yet.";

        const reports = listResults(reportsPayload).slice(0, 8);
        document.querySelector("[data-student-reports]").innerHTML = reports.length
            ? `<table><thead><tr><th>Week</th><th>Dates</th><th>Status</th><th>Submitted</th></tr></thead><tbody>${reports.map((report) => `<tr><td>Week ${escapeHtml(report.week_number)}</td><td>${formatDate(report.week_start_date)} — ${formatDate(report.week_end_date)}</td><td>${status(report.status)}</td><td>${report.submitted_at ? formatDate(report.submitted_at.slice(0, 10)) : "—"}</td></tr>`).join("")}</tbody></table>`
            : emptyState("No weekly reports have been created for this placement.");
    }

    function renderSupervisor(data) {
        selectors.metrics.innerHTML = [
            metric("Assigned students", data.total_assigned_students, "Across all placements"),
            metric("Active placements", data.active_placements, "Currently in progress", "var(--blue)"),
            metric("Awaiting review", data.submitted_reports_awaiting_review, "Submitted reports", "var(--orange)"),
            metric("Reviewed reports", data.reviewed_reports, "Completed reviews", "var(--green)"),
        ].join("");

        document.querySelector("[data-supervisor-view]").hidden = false;
        const reports = data.recent_submissions || [];
        document.querySelector("[data-supervisor-reports]").innerHTML = reports.length
            ? `<table><thead><tr><th>Student</th><th>Registration</th><th>Week</th><th>Status</th><th>Submitted</th></tr></thead><tbody>${reports.map((report) => `<tr><td>${escapeHtml(report.student_name)}</td><td>${escapeHtml(report.registration_number)}</td><td>Week ${escapeHtml(report.week_number)}</td><td>${status(report.status)}</td><td>${report.submitted_at ? formatDate(report.submitted_at.slice(0, 10)) : "—"}</td></tr>`).join("")}</tbody></table>`
            : emptyState("No submitted or reviewed reports are available yet.");
    }

    function renderAdmin(data) {
        selectors.metrics.innerHTML = [
            metric("Students", data.total_students, "Registered profiles"),
            metric("Supervisors", data.total_supervisors, "Registered profiles", "var(--blue)"),
            metric("Active placements", data.active_placements, `${data.total_placements} total placements`, "var(--green)"),
            metric("Pending reviews", data.pending_reviews, `${data.reviewed_reports} reports reviewed`, "var(--orange)"),
        ].join("");

        document.querySelector("[data-admin-view]").hidden = false;
        const progress = data.submission_progress_per_student || [];
        document.querySelector("[data-admin-progress]").innerHTML = progress.length
            ? `<table><thead><tr><th>Student</th><th>Registration</th><th>Expected</th><th>Submitted</th><th>Progress</th><th>Overdue</th></tr></thead><tbody>${progress.map((item) => `<tr><td>${escapeHtml(item.student_name)}</td><td>${escapeHtml(item.registration_number)}</td><td>${escapeHtml(item.expected_reports_to_date)}</td><td>${escapeHtml(item.submitted_reports_to_date)}</td><td><strong>${escapeHtml(item.submission_percentage)}%</strong></td><td>${item.overdue_weeks?.length ? escapeHtml(item.overdue_weeks.join(", ")) : "—"}</td></tr>`).join("")}</tbody></table>`
            : emptyState("No active placements are available for progress reporting.");

        const overdue = data.students_with_overdue_reports || [];
        document.querySelector("[data-overdue-students]").innerHTML = overdue.length
            ? `<div class="risk-list">${overdue.slice(0, 8).map((item) => `<div class="risk-item"><strong>${escapeHtml(item.student_name)}</strong><small>Weeks ${escapeHtml(item.overdue_weeks.join(", "))} overdue</small></div>`).join("")}</div>`
            : emptyState("No students currently have overdue reports.");
    }

    function roleConfiguration(role) {
        const configurations = {
            STUDENT: {
                endpoint: "/api/v1/dashboard/student/",
                eyebrow: "Student workspace",
                intro: "Track your placement, weekly submissions, and supervisor feedback.",
            },
            SUPERVISOR: {
                endpoint: "/api/v1/dashboard/supervisor/",
                eyebrow: "Supervisor workspace",
                intro: "Review assigned-student activity and keep feedback moving.",
            },
            ADMIN: {
                endpoint: "/api/v1/dashboard/admin/",
                eyebrow: "Administrator workspace",
                intro: "Monitor people, placements, reports, and cohort progress.",
            },
        };
        return configurations[role];
    }

    async function loadDashboard() {
        selectors.loading.hidden = false;
        selectors.content.hidden = true;
        selectors.error.hidden = true;
        document.querySelectorAll("[data-student-view], [data-supervisor-view], [data-admin-view]").forEach((view) => { view.hidden = true; });

        try {
            const user = await request("/api/v1/auth/me/");
            const configuration = roleConfiguration(user.role);
            if (!configuration) throw new Error("This account does not have a supported role.");

            document.querySelector("[data-greeting]").textContent = greeting();
            document.querySelector("[data-dashboard-name]").textContent = user.first_name || user.full_name || "there";
            document.querySelector("[data-dashboard-eyebrow]").textContent = configuration.eyebrow;
            document.querySelector("[data-dashboard-intro]").textContent = configuration.intro;

            const dashboardPromise = request(configuration.endpoint);
            const reportsPromise = user.role === "STUDENT" ? request("/api/v1/reports/?ordering=-week_start_date") : Promise.resolve(null);
            const [dashboard, reports] = await Promise.all([dashboardPromise, reportsPromise]);

            if (user.role === "STUDENT") renderStudent(dashboard, reports);
            if (user.role === "SUPERVISOR") renderSupervisor(dashboard);
            if (user.role === "ADMIN") renderAdmin(dashboard);
            selectors.content.hidden = false;
        } catch (error) {
            selectors.error.hidden = false;
            selectors.errorMessage.textContent = error.message || "Please sign in again and retry.";
            if (error.status === 401) window.ITS.clearSession();
        } finally {
            selectors.loading.hidden = true;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        if (!window.ITS.getStoredUser()) {
            window.location.replace("/login/?next=/dashboard/");
            return;
        }
        loadDashboard();
        document.querySelector("[data-refresh-dashboard]")?.addEventListener("click", loadDashboard);
    });
}());
