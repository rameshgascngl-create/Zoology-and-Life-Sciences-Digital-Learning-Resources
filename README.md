[README(4).md](https://github.com/user-attachments/files/31094188/README.4.md)
# Animal Physiology Learning Hub

An advanced, browser-based learning resource for **B.Sc. Zoology animal physiology**. The application combines structured lessons, comparative and integrative physiology, bilingual learning support, diagrams, formative assessment, revision tools, and quantitative physiology exercises in one portable HTML file.

**Current release:** v2.7.1 — Chrome Offline Stable  
**Application file:** [`Animal_Physiology_Learning_Hub_v2.7.1_Chrome_Offline_Stable.html`](Animal_Physiology_Learning_Hub_v2.7.1_Chrome_Offline_Stable.html)

## Highlights

- 57 syllabus-aligned lessons across four units
- 10 advanced physiology masterclasses
- 14 embedded mechanism and concept diagrams
- 283 question-and-answer paths
- Tamil lesson explanations in expandable sections
- Comparative, adaptive, environmental, clinical, and experimental perspectives
- Knowledge graph and concept-linked learning pathways
- MCQs, flashcards, glossary, assessments, notes, and a study timer
- Cardiovascular and renal physiology calculators
- Responsive interface for desktop and mobile browsers
- Dark mode, keyboard navigation, print support, and reduced-motion support
- Local progress storage with no account or server requirement
- Deferred indexing and topic-level resource loading for faster Chrome startup

## Course Coverage

| Unit | Major area |
|---|---|
| I | Nutrition and Respiration |
| II | Circulation and Excretion |
| III | Neuromuscular Co-ordination |
| IV | Endocrine Glands and Receptors |

The advanced layer extends the core syllabus through allometry, thermal physiology, osmoregulation, hypoxia, exercise physiology, stress physiology, chronophysiology, homeostatic control, integrative physiology, and experimental methods.

## Learning Tools

- **Lessons:** mechanism-centred explanations, misconceptions, clinical links, examination guidance, and advanced bridges
- **Diagrams:** embedded illustrations that work without a network connection
- **Knowledge graph:** connections among concepts, mechanisms, systems, and units
- **Assessment:** MCQs and structured evidence tasks with immediate feedback
- **Revision:** flashcards, glossary, topic search, progress tracking, and study notes
- **Calculators:** cardiac output, pulse pressure, mean arterial pressure, creatinine clearance, generic renal clearance, and filtered load
- **Accessibility:** semantic controls, visible keyboard focus, ARIA labels, adaptable colour themes, and print-friendly lesson views

## Run the Application

No installation, build tool, package manager, or web server is required.

1. Download the HTML file.
2. Open it with a current version of Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari.
3. Allow the Home screen to appear before beginning navigation, especially on lower-memory mobile devices.

For the most reliable Android experience, save the file to the device first and open it from the **Files** app using Chrome. Avoid repeatedly opening the same file from a messaging-app preview.

## Offline Behaviour

The following resources are embedded and work offline:

- Lessons
- Diagrams
- Quizzes
- Flashcards
- Notes
- Glossary
- Simulators and calculators
- Assessments

External readings, videos, and recommended websites are not embedded; they require an internet connection. Pending external resources are labelled as such within the application and should not be interpreted as verified offline content.

## GitHub Pages Deployment

To publish the app as a website:

1. Place the HTML file and this `README.md` in the repository root.
2. Rename the HTML file to `index.html`.
3. Open **Repository Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Choose the `main` branch and the `/ (root)` folder, then save.
6. Open the GitHub Pages address shown after deployment completes.

If the original versioned filename is retained, users can still open it through a direct repository or Pages link, but `index.html` is recommended for a clean site address.

## Suggested Repository Structure

```text
.
├── index.html
├── README.md
└── LICENSE
```

The complete application remains inside `index.html`; no external JavaScript, CSS, font, image, or CDN dependency is required for its core offline features.

## Technical Notes

- Single-file HTML, CSS, JavaScript, and inline SVG architecture
- Mobile-first responsive layout
- Search indexing is created only when search is used
- Topic resources are loaded only when the relevant lesson is opened
- Hash-based navigation protects in-app Back behaviour during `file://` use
- User notes, theme, completion state, and selected progress data are stored locally in the browser
- Clearing browser site data or local storage removes locally saved progress and notes

## Verified Release Status

The v2.7.1 release was regression-tested with the following results:

| Check | Result |
|---|---:|
| Lessons rendered | 57/57 |
| Application views | 18/18 |
| Question-answer paths | 283/283 |
| Offline resource types | 8/8 |
| JavaScript startup errors | 0 |
| Knowledge-graph defects | 0 |

The release was also tested under an Android-style `file://` launch. Actual performance can vary with browser version, device memory, and storage provider.

## Educational Use

This resource is intended for teaching, guided study, revision, and formative assessment. It does not replace prescribed university textbooks, laboratory instruction, institutional assessment rules, or professional medical advice.

## Privacy and Local Data

The core application does not require registration and does not send notes or progress to a server. Learning data is stored in the browser on the user’s device. Opening an external resource leaves the offline application and is subject to that website’s own privacy policy.

## Author and Institution

Compiled by **R. Ramesh**  
Department of Zoology  
Government Arts and Science College, Nagercoil, Tamil Nadu, India

## License

No open-source licence is currently specified. Add a `LICENSE` file before permitting copying, modification, or redistribution beyond applicable educational and legal exceptions.

## Citation

Suggested citation:

> Ramesh, R. (2026). *Animal Physiology Learning Hub* (Version 2.7.1) [Single-file web application]. Department of Zoology, Government Arts and Science College, Nagercoil.

