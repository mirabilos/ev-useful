-- Drop everything from the PostgreSQL database.
-- Run this while the tomcat service is stopped!
-- Release: ${project.version}

DO $$
DECLARE
	r RECORD;
BEGIN
	FOR r IN (SELECT pt.tgname, pns.nspname, pc.relname
		FROM pg_trigger pt, pg_class pc, pg_namespace pns
		WHERE pc.oid=pt.tgrelid AND pns.oid=pc.relnamespace
		    AND tgisinternal=false
	    ) LOOP
		EXECUTE format('DROP TRIGGER %I ON %I.%I;',
		    r.tgname, r.nspname, r.relname);
	END LOOP;
-- …
END; $$;


-- Exklusionen: https://stackoverflow.com/a/11462481/2171120
