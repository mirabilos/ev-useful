For the cases where you can’t just `DROP SCHEMA public CASCADE;`, `DROP OWNED BY current_user;` or something, here’s a stand-alone SQL script I wrote, which is transaction-safe (i.e. you can put it between `BEGIN;` and either `ROLLBACK;` to just test it out or `COMMIT;` to actually do the deed) and cleans up “all” database objects… well, all those used in the database our application uses or I could sensibly add, which is:

 - triggers on tables
 - constraints on tables (FK, PK, `CHECK`, `UNIQUE`)
 - indicēs
 - `VIEW`s (normal or materialised)
 - tables
 - sequences
 - functions / procedures ([`pg_proc.proisagg`](https://www.postgresql.org/docs/current/catalog-pg-proc.html) probably [should be honoured](https://stackoverflow.com/a/12127714/2171120) though)
 - all nōn-default (i.e. not `public` or DB-internal) schemata “we” own: the script is useful when run as “not a database superuser”; a superuser can drop _all_ schemata (the really important ones are still explicitly excluded, though)

Not dropped are (some deliberate; some only because I had no example in our DB):

 - the `public` schema (e.g. for extension-provided stuff in them)
 - extensions
 - aggregate functions
 - collations and other locale stuff
 - event triggers
 - text search stuff, … (see [here](https://www.postgresql.org/docs/current/catalogs-overview.html) for other stuff I might have missed)
 - roles or other security settings
 - composite types
 - toast tables
 - FDW and foreign tables

I’ve also got a version which deletes “everything except two tables and what belongs to them” in case someone is interested; the diff is small. Contact me if necessary.

## SQL

    -- Copyright © 2019
    --      mirabilos <t.glaser@tarent.de>
    --
    -- Provided that these terms and disclaimer and all copyright notices
    -- are retained or reproduced in an accompanying document, permission
    -- is granted to deal in this work without restriction, including un‐
    -- limited rights to use, publicly perform, distribute, sell, modify,
    -- merge, give away, or sublicence.
    --
    -- This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
    -- the utmost extent permitted by applicable law, neither express nor
    -- implied; without malicious intent or gross negligence. In no event
    -- may a licensor, author or contributor be held liable for indirect,
    -- direct, other damage, loss, or other issues arising in any way out
    -- of dealing in the work, even if advised of the possibility of such
    -- damage or existence of a defect, except proven that it results out
    -- of said person’s immediate fault when using the work as intended.
    -- -
    -- Drop everything from the PostgreSQL database.
    
    DO $$
    DECLARE
            r RECORD;
    BEGIN
            -- triggers
            FOR r IN (SELECT pns.nspname, pc.relname, pt.tgname
                    FROM pg_trigger pt, pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace AND pc.oid=pt.tgrelid
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pt.tgisinternal=false
                ) LOOP
                    EXECUTE format('DROP TRIGGER %I ON %I.%I;',
                        r.tgname, r.nspname, r.relname);
            END LOOP;
            -- constraints #1: foreign key
            FOR r IN (SELECT pns.nspname, pc.relname, pcon.conname
                    FROM pg_constraint pcon, pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace AND pc.oid=pcon.conrelid
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pcon.contype='f'
                ) LOOP
                    EXECUTE format('ALTER TABLE ONLY %I.%I DROP CONSTRAINT %I;',
                        r.nspname, r.relname, r.conname);
            END LOOP;
            -- constraints #2: the rest
            FOR r IN (SELECT pns.nspname, pc.relname, pcon.conname
                    FROM pg_constraint pcon, pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace AND pc.oid=pcon.conrelid
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pcon.contype<>'f'
                ) LOOP
                    EXECUTE format('ALTER TABLE ONLY %I.%I DROP CONSTRAINT %I;',
                        r.nspname, r.relname, r.conname);
            END LOOP;
            -- indicēs
            FOR r IN (SELECT pns.nspname, pc.relname
                    FROM pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pc.relkind='i'
                ) LOOP
                    EXECUTE format('DROP INDEX %I.%I;',
                        r.nspname, r.relname);
            END LOOP;
            -- normal and materialised views
            FOR r IN (SELECT pns.nspname, pc.relname
                    FROM pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pc.relkind IN ('v', 'm')
                ) LOOP
                    EXECUTE format('DROP VIEW %I.%I;',
                        r.nspname, r.relname);
            END LOOP;
            -- tables
            FOR r IN (SELECT pns.nspname, pc.relname
                    FROM pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pc.relkind='r'
                ) LOOP
                    EXECUTE format('DROP TABLE %I.%I;',
                        r.nspname, r.relname);
            END LOOP;
            -- sequences
            FOR r IN (SELECT pns.nspname, pc.relname
                    FROM pg_class pc, pg_namespace pns
                    WHERE pns.oid=pc.relnamespace
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                        AND pc.relkind='S'
                ) LOOP
                    EXECUTE format('DROP SEQUENCE %I.%I;',
                        r.nspname, r.relname);
            END LOOP;
            -- functions / procedures
            FOR r IN (SELECT pns.nspname, pp.proname, pp.oid
                    FROM pg_proc pp, pg_namespace pns
                    WHERE pns.oid=pp.pronamespace
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ) LOOP
                    EXECUTE format('DROP FUNCTION %I.%I(%s);',
                        r.nspname, r.proname,
                        pg_get_function_identity_arguments(r.oid));
            END LOOP;
            -- nōn-default schemata we own; assume to be run by a not-superuser
            FOR r IN (SELECT pns.nspname
                    FROM pg_namespace pns, pg_roles pr
                    WHERE pr.oid=pns.nspowner
                        AND pns.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
                        AND pr.rolname=current_user
                ) LOOP
                    EXECUTE format('DROP SCHEMA %I;', r.nspname);
            END LOOP;
            -- voilà
            RAISE NOTICE 'Database cleared!';
    END; $$;

Tested on PostgreSQL 9.6 (`jessie-backports`). Bugfixes and further improvements welcome!
