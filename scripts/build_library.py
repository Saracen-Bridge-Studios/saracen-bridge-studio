"""Build the deduplicated source library from extracted plugin bundles. Files are copied, never modified."""
import hashlib, json, shutil, sys, pathlib
S = pathlib.Path(sys.argv[1]); R = pathlib.Path(sys.argv[2])
TOOLS = {  # bundle dir -> tool slug
 'gpt-9b2cd882216a358964120caa14fa52f8':'fpm_finance_plan_modeller',
 'gpt-60858caf9b72b55ecebbf3e524717452':'t01_look_book',
 'gpt-c1e22e0ce4851f4909ed62a9daaf1fe6':'t02_script_coverage',
 'gpt-6a7a037b7b731791e44f69eb3f5d5736_1':'t03_schedule_budget',
 'gpt-131fd26bbddeb641a570d494a545863b':'t04_sales_agent',
 'gpt-daa7a0e949ceb7fcdd60e0ba3ed11b79':'t05_brand_integration',
 'gpt-22026f19dc5335965ad0fc7841a26976':'t06_location_incentive',
 'gpt-f0f93317666f626a07a1336cd2ff6436':'t07_bfi_certification',
 'gpt-ab0a539ea4413da19ab5f0b3a051b6b4_1':'t08_film_finance_greenlight',
 'gpt-672013c89c35e35820953bda3c82ea97':'t09_film_finance_dataroom',
 'saracen-bridge-production-agreement-builder_1':'t10_agreement_builder',
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
seen = {}  # hash -> list of (tool, relpath)
for d, tool in TOOLS.items():
    for f in sorted((S/'plugins'/d).rglob('*')):
        if f.is_file(): seen.setdefault(sha(f), []).append((tool, f, f.relative_to(S/'plugins'/d)))
manifest = []
for h, uses in seen.items():
    tools = sorted({t for t,_,_ in uses}); f = uses[0][1]
    shared = len(tools) > 1
    dest = R/'sources'/('shared' if shared else tools[0])/(f.name if shared else uses[0][2])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(f, dest)
    assert sha(dest) == h
    manifest.append({'path': str(dest.relative_to(R)), 'sha256': h, 'bytes': dest.stat().st_size, 'used_by': tools})
# behaviour captures and chat-recovered artefacts (FPM)
extra = R/'sources'/'captures'; extra.mkdir(exist_ok=True)
U = pathlib.Path('/root/.claude/uploads/7a598364-bb96-5dfd-b44c-07e48c165f2d')
for src, name in [('706b411c-Saracen_Bridge_Financial_Modeller_Standalone_Specification.md','FPM_chat_reconstructed_spec.md'),
                  ('382f0bf1-SHADE_Spain_Finance_Model_Audited_v3.xlsx','FPM_capture_SHADE_audit_v3.xlsx'),
                  ('718c3e83-SHADE_Finance_Viability_Report_12_October_2026.docx','FPM_capture_SHADE_viability_report.docx')]:
    shutil.copy2(U/src, extra/name)
    manifest.append({'path': f'sources/captures/{name}', 'sha256': sha(extra/name), 'bytes': (extra/name).stat().st_size, 'used_by': ['fpm_finance_plan_modeller'], 'kind': 'behaviour_capture'})
manifest.sort(key=lambda m: m['path'])
(R/'sources'/'MANIFEST.json').write_text(json.dumps(manifest, indent=1))
print(len(manifest), 'files;', sum(1 for m in manifest if len(m['used_by'])>1), 'shared')
