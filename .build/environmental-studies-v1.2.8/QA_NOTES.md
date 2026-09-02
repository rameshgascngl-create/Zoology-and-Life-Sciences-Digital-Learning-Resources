# v1.2.8 QA

Primary acceptance criteria on Android handset:

- Native Contents, Previous, Next, Visual, Privacy, English and Tamil controls respond independently of HTML touch handling.
- WebView scrolls vertically through long pages with one-finger scrolling.
- HTML book toolbar is hidden on phone viewports.
- No swipe-to-turn touch listener competes with vertical scrolling.
- Tamil switching is invoked by native Android click handler calling `setLang('ta')`.
