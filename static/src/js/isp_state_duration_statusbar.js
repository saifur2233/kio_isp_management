/** @odoo-module **/

import { registry } from "@web/core/registry";
import { StatusBarField, statusBarField } from "@web/views/fields/statusbar/statusbar_field";
import { useState, onWillUnmount } from "@odoo/owl";

export class IspStateDurationStatusBar extends StatusBarField {
    static template = "kio_isp_management.IspStateDurationStatusBar";

    setup() {
        super.setup();
        this._tick = useState({ n: 0 });

        // Stopwatch-like refresh with milliseconds.
        this._timer = setInterval(() => {
            this._tick.n++;
        }, 100);

        onWillUnmount(() => clearInterval(this._timer));
    }

    _pad2(value) {
        return String(value).padStart(2, "0");
    }

    _formatStopwatch(ms) {
        let totalMs = Number(ms || 0);
        if (!Number.isFinite(totalMs) || totalMs < 0) {
            totalMs = 0;
        }
        totalMs = Math.floor(totalMs);

        const hours = Math.floor(totalMs / 3600000);
        const minutes = Math.floor((totalMs % 3600000) / 60000);
        const seconds = Math.floor((totalMs % 60000) / 1000);
        // Show 2-digit sub-seconds (centiseconds) in stopwatch label.
        const centiseconds = Math.floor((totalMs % 1000) / 10);
        return `${this._pad2(hours)}:${this._pad2(minutes)}:${this._pad2(seconds)}.${this._pad2(centiseconds)}`;
    }

    _diffMs(startDate, endDate) {
        if (!startDate || !endDate) {
            return null;
        }
        return Math.max(0, endDate.getTime() - startDate.getTime());
    }

    _toDate(val) {
        if (!val) return null;
        if (val instanceof Date) return val;
        if (typeof val === "string") {
            // "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SS"
            return new Date(val.replace(" ", "T"));
        }
        if (typeof val.toJSDate === "function") {
            return val.toJSDate();
        }
        const parsed = new Date(val);
        return Number.isNaN(parsed.getTime()) ? null : parsed;
    }

    _getSurveyStateDurationMs(stateValue, data) {
        const now = new Date();
        const draftAt = this._toDate(data.state_draft_date) || this._toDate(data.create_date);
        const doneAt = this._toDate(data.state_done_date);
        const workAt = this._toDate(data.state_work_order_date);
        const workStopAt = this._toDate(data.state_work_order_stop_date);

        if (stateValue === "draft") {
            if (data.state === "draft" && draftAt) {
                return this._diffMs(draftAt, now);
            }
            if (draftAt && doneAt) {
                return this._diffMs(draftAt, doneAt);
            }
            if (Number.isFinite(data.dur_draft_to_done_sec)) {
                return Math.max(0, Number(data.dur_draft_to_done_sec)) * 1000;
            }
        }

        if (stateValue === "done") {
            if (data.state === "done" && doneAt) {
                return this._diffMs(doneAt, now);
            }
            if (doneAt && workAt) {
                return this._diffMs(doneAt, workAt);
            }
            if (Number.isFinite(data.dur_done_to_work_sec)) {
                return Math.max(0, Number(data.dur_done_to_work_sec)) * 1000;
            }
        }

        if (stateValue === "work_order") {
            if (data.state === "work_order" && workAt && !workStopAt) {
                return this._diffMs(workAt, now);
            }
            if (workAt && workStopAt) {
                return this._diffMs(workAt, workStopAt);
            }
            if (Number.isFinite(data.dur_work_order_active_sec)) {
                return Math.max(0, Number(data.dur_work_order_active_sec)) * 1000;
            }
        }

        return null;
    }

    _getSurveyItems(items, data) {
        return items.map((it) => {
            let extra = "";
            const durationMs = this._getSurveyStateDurationMs(it.value, data);
            if (durationMs !== null) {
                extra = this._formatStopwatch(durationMs);
            }

            const baseLabel = it.label;
            const label = extra ? `${baseLabel} (${extra})` : baseLabel;
            return { ...it, label, baseLabel, extraDuration: extra };
        });
    }

    _getWorkStateDateMap(data) {
        const workOrderStartedAt =
            this._toDate(data.work_state_work_order_date) ||
            this._toDate(data.state_work_order_date) ||
            this._toDate(data.create_date);
        return {
            work_order: workOrderStartedAt,
            sell_confirm: this._toDate(data.work_state_sell_confirm_date),
            marketing_confirm: this._toDate(data.work_state_marketing_confirm_date),
            marketing_revert: this._toDate(data.work_state_marketing_revert_date),
            legal_confirm: this._toDate(data.work_state_legal_confirm_date),
            legal_revert: this._toDate(data.work_state_legal_revert_date),
        };
    }

    _getWorkRunningDuration(data, stateDates) {
        const state = data.work_state;
        const startedAt = stateDates[state];
        if (!startedAt) {
            return null;
        }
        const now = new Date();
        return { state, ms: this._diffMs(startedAt, now) };
    }

    _getNextStateDate(currentDate, stateDates) {
        if (!currentDate) {
            return null;
        }
        let nextDate = null;
        for (const dt of Object.values(stateDates)) {
            if (!dt || dt <= currentDate) {
                continue;
            }
            if (!nextDate || dt < nextDate) {
                nextDate = dt;
            }
        }
        return nextDate;
    }

    _getWorkItems(items, data) {
        const stateDates = this._getWorkStateDateMap(data);
        const running = this._getWorkRunningDuration(data, stateDates);

        return items.map((it) => {
            let extra = "";
            const stateValue = it.value;

            const startedAt = stateDates[stateValue];
            if (data.work_state === stateValue && running?.state === stateValue) {
                extra = this._formatStopwatch(running.ms);
            } else if (startedAt) {
                const nextAt = this._getNextStateDate(startedAt, stateDates);
                if (nextAt) {
                    const ms = this._diffMs(startedAt, nextAt);
                    extra = this._formatStopwatch(ms);
                }
            }

            const baseLabel = it.label;
            const label = extra ? `${baseLabel} (${extra})` : baseLabel;
            return { ...it, label, baseLabel, extraDuration: extra };
        });
    }

    getAllItems() {
        // trigger rerender
        this._tick.n;

        const items = super.getAllItems();
        const data = this.props.record.data;
        if (this.props.name === "work_state") {
            return this._getWorkItems(items, data);
        }
        return this._getSurveyItems(items, data);
    }
}

registry.category("fields").add("isp_state_duration_statusbar", {
    ...statusBarField,
    component: IspStateDurationStatusBar,
    additionalClasses: [...(statusBarField.additionalClasses || []), "o_field_statusbar"],
});
