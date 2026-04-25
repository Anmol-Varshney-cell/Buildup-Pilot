-- Check count of new problems
SELECT COUNT(*) as total_problems FROM Problem;
SELECT COUNT(*) as html_problems FROM Problem WHERE slug LIKE 'html-%' OR slug LIKE 'css-%' OR slug LIKE 'js-%';
SELECT COUNT(*) as dbms_problems FROM Problem WHERE slug LIKE 'dbms-%';
SELECT slug, title FROM Problem WHERE slug LIKE 'html-%' OR slug LIKE 'css-%' OR slug LIKE 'js-%' OR slug LIKE 'dbms-%' LIMIT 5;
