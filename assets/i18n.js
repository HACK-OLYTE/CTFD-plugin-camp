/**
 * CampI18n - Internationalization for the CTFd Camps plugin
 * Supports: English (en), French (fr), Spanish (es), German (de)
 * Default: English
 */
var CampI18n = (function () {

    var translations = {
        en: {
            // Page
            camp_selection_title: '🎯 Camp Selection',
            camp_selection_subtitle: 'Choose your camp to participate in the CTF',
            plugin_by: 'Plugin developed by',

            // Camp names
            blue_camp: 'Blue Camp',
            red_camp: 'Red Camp',
            defenders: 'Defenders',
            attackers: 'Attackers',
            teams_label: 'team(s)',

            // Statistics
            current_distribution: '📊 Current team distribution',

            // Current camp
            your_current_camp: 'Your current camp',
            no_camp_selected: 'No camp selected',
            no_camp_warning: 'You must choose a camp to access challenges!',

            // Deadline
            deadline_notice_label: 'Notice',
            deadline_passed_label: 'Deadline passed',
            can_change_until: 'You can change your camp until',
            deadline_was: 'The deadline was',

            // Change blocked
            change_blocked: 'Camp change blocked',

            // Camp descriptions
            blue_camp_desc: 'Protect systems and infrastructure against attacks. Analyze logs, harden security, detect intrusions.',
            blue_item1: 'Defense challenges',
            blue_item2: 'Forensics analysis',
            blue_item3: 'Incident detection',

            red_camp_desc: 'Exploit vulnerabilities and penetrate adversary systems. Find flaws, develop exploits, bypass protections.',
            red_item1: 'Offensive challenges',
            red_item2: 'Vulnerability exploitation',
            red_item3: 'Offensive pentesting',

            // Challenges page badge
            you_are_in: 'You are in the',
            change_camp_btn: 'Change camp',

            // Buttons
            current_camp_btn: 'Current camp',
            camp_full: 'Camp full',
            limited_to: 'limited to',
            change_locked: 'Change locked',
            join_blue: 'Join Blue Camp',
            join_red: 'Join Red Camp',

            // JS dialogs
            confirm_join: 'Are you sure you want to join the {camp}?',
            error_label: 'Error',
            select_error: 'Error selecting camp',
        },

        fr: {
            // Page
            camp_selection_title: '🎯 Choix du Camp',
            camp_selection_subtitle: 'Choisissez votre camp pour participer au CTF',
            plugin_by: 'Plugin développé par',

            // Camp names
            blue_camp: 'Camp Bleu',
            red_camp: 'Camp Rouge',
            defenders: 'Défenseurs',
            attackers: 'Attaquants',
            teams_label: 'équipe(s)',

            // Statistics
            current_distribution: '📊 Répartition actuelle des équipes',

            // Current camp
            your_current_camp: 'Votre camp actuel',
            no_camp_selected: 'Aucun camp sélectionné',
            no_camp_warning: 'Vous devez choisir un camp pour accéder aux challenges !',

            // Deadline
            deadline_notice_label: 'Attention',
            deadline_passed_label: 'Date limite dépassée',
            can_change_until: 'Vous pouvez changer de camp jusqu\'au',
            deadline_was: 'La date limite était le',

            // Change blocked
            change_blocked: 'Changement de camp bloqué',

            // Camp descriptions
            blue_camp_desc: 'Protégez les systèmes et infrastructures contre les attaques. Analysez les logs, renforcez la sécurité, détectez les intrusions.',
            blue_item1: 'Challenges de défense',
            blue_item2: 'Analyse forensics',
            blue_item3: 'Détection d\'incidents',

            red_camp_desc: 'Exploitez les vulnérabilités et pénétrez les systèmes adverses. Trouvez les failles, développez des exploits, contournez les protections.',
            red_item1: 'Challenges d\'attaque',
            red_item2: 'Exploitation de vulnérabilités',
            red_item3: 'Pentest offensif',

            // Challenges page badge
            you_are_in: 'Vous êtes dans le',
            change_camp_btn: 'Changer de camp',

            // Buttons
            current_camp_btn: 'Camp actuel',
            camp_full: 'Camp complet',
            limited_to: 'limité à',
            change_locked: 'Changement bloqué',
            join_blue: 'Rejoindre le Camp Bleu',
            join_red: 'Rejoindre le Camp Rouge',

            // JS dialogs
            confirm_join: 'Êtes-vous sûr de vouloir rejoindre le {camp} ?',
            error_label: 'Erreur',
            select_error: 'Erreur lors de la sélection du camp',
        },

        es: {
            camp_selection_title: '🎯 Selección de Campo',
            camp_selection_subtitle: 'Elige tu campo para participar en el CTF',
            plugin_by: 'Plugin desarrollado por',
            blue_camp: 'Campo Azul',
            red_camp: 'Campo Rojo',
            defenders: 'Defensores',
            attackers: 'Atacantes',
            teams_label: 'equipo(s)',
            current_distribution: '📊 Distribución actual de equipos',
            your_current_camp: 'Tu campo actual',
            no_camp_selected: 'Ningún campo seleccionado',
            no_camp_warning: '¡Debes elegir un campo para acceder a los desafíos!',
            deadline_notice_label: 'Aviso',
            deadline_passed_label: 'Plazo vencido',
            can_change_until: 'Puedes cambiar de campo hasta el',
            deadline_was: 'El plazo era el',
            change_blocked: 'Cambio de campo bloqueado',
            blue_camp_desc: 'Protege sistemas e infraestructuras contra ataques. Analiza logs, refuerza la seguridad, detecta intrusiones.',
            blue_item1: 'Desafíos de defensa',
            blue_item2: 'Análisis forense',
            blue_item3: 'Detección de incidentes',
            red_camp_desc: 'Explota vulnerabilidades y penetra sistemas adversarios. Encuentra fallos, desarrolla exploits, elude protecciones.',
            red_item1: 'Desafíos ofensivos',
            red_item2: 'Explotación de vulnerabilidades',
            red_item3: 'Pentesting ofensivo',
            you_are_in: 'Estás en el',
            change_camp_btn: 'Cambiar de campo',
            current_camp_btn: 'Campo actual',
            camp_full: 'Campo lleno',
            limited_to: 'limitado a',
            change_locked: 'Cambio bloqueado',
            join_blue: 'Unirse al Campo Azul',
            join_red: 'Unirse al Campo Rojo',
            confirm_join: '¿Estás seguro de que quieres unirte a {camp}?',
            error_label: 'Error',
            select_error: 'Error al seleccionar el campo',
        },

        de: {
            camp_selection_title: '🎯 Lager-Auswahl',
            camp_selection_subtitle: 'Wähle dein Lager für den CTF',
            plugin_by: 'Plugin entwickelt von',
            blue_camp: 'Blaues Lager',
            red_camp: 'Rotes Lager',
            defenders: 'Verteidiger',
            attackers: 'Angreifer',
            teams_label: 'Team(s)',
            current_distribution: '📊 Aktuelle Team-Verteilung',
            your_current_camp: 'Dein aktuelles Lager',
            no_camp_selected: 'Kein Lager ausgewählt',
            no_camp_warning: 'Du musst ein Lager wählen, um auf Challenges zuzugreifen!',
            deadline_notice_label: 'Hinweis',
            deadline_passed_label: 'Frist abgelaufen',
            can_change_until: 'Du kannst dein Lager wechseln bis',
            deadline_was: 'Die Frist war am',
            change_blocked: 'Lagerwechsel blockiert',
            blue_camp_desc: 'Schütze Systeme und Infrastruktur vor Angriffen. Analysiere Logs, härte Sicherheit, erkenne Eindringlinge.',
            blue_item1: 'Verteidigungs-Challenges',
            blue_item2: 'Forensik-Analyse',
            blue_item3: 'Vorfalls-Erkennung',
            red_camp_desc: 'Nutze Schwachstellen aus und dringe in gegnerische Systeme ein. Finde Lücken, entwickle Exploits, umgehe Schutzmaßnahmen.',
            red_item1: 'Offensive Challenges',
            red_item2: 'Schwachstellen-Ausnutzung',
            red_item3: 'Offensives Pentesting',
            you_are_in: 'Du bist im',
            change_camp_btn: 'Lager wechseln',
            current_camp_btn: 'Aktuelles Lager',
            camp_full: 'Lager voll',
            limited_to: 'begrenzt auf',
            change_locked: 'Wechsel gesperrt',
            join_blue: 'Blaues Lager beitreten',
            join_red: 'Rotes Lager beitreten',
            confirm_join: 'Bist du sicher, dass du {camp} beitreten möchtest?',
            error_label: 'Fehler',
            select_error: 'Fehler bei der Lagerauswahl',
        }
    };

    /**
     * Detect language from cookie or browser settings.
     * Checks: `lang` cookie → `locale` cookie → browser language → 'en'
     * Handles formats like "fr", "fr-FR", "fr_FR"
     */
    function getLang() {
        // Check cookies (handles "lang=fr", "lang=fr-FR", "lang=fr_FR")
        var cookieNames = ['lang', 'locale', 'language'];
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var parts = cookies[i].trim().split('=');
            var name = parts[0].trim();
            if (cookieNames.indexOf(name) !== -1 && parts[1]) {
                var lang = parts[1].trim().split(/[-_]/)[0].toLowerCase();
                if (translations[lang]) return lang;
            }
        }
        // Check browser language (navigator.languages takes priority over navigator.language)
        var langs = navigator.languages || [navigator.language || navigator.userLanguage || 'en'];
        for (var j = 0; j < langs.length; j++) {
            var l = langs[j].split(/[-_]/)[0].toLowerCase();
            if (translations[l]) return l;
        }
        return 'en';
    }

    /**
     * Translate a key. Falls back to English if missing in current language.
     */
    function t(key) {
        var lang = getLang();
        var dict = translations[lang] || translations['en'];
        return dict[key] !== undefined ? dict[key] : (translations['en'][key] || key);
    }

    /**
     * Apply translations to all data-i18n / data-i18n-html / data-i18n-placeholder elements.
     */
    function apply() {
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            el.textContent = t(el.getAttribute('data-i18n'));
        });
        document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
            el.innerHTML = t(el.getAttribute('data-i18n-html'));
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
        });
    }

    document.addEventListener('DOMContentLoaded', apply);

    return { t: t, apply: apply, getLang: getLang };

})();
