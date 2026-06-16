from pathlib import Path

import aiosqlite


USER_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
KB_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


async def test_create_pool_upgrades_documents_missing_knowledge_base_id(tmp_path: Path):
    from infra.db.sqlite import SQLiteDocumentRepository, create_pool

    db_path = tmp_path / "index.db"
    old_db = await aiosqlite.connect(str(db_path))
    await old_db.executescript(
        """
        CREATE TABLE workspace (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            user_id TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(user_id)
        );
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            title TEXT,
            path TEXT DEFAULT '/' NOT NULL,
            relative_path TEXT NOT NULL,
            source_kind TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            document_number INTEGER,
            status TEXT DEFAULT 'pending',
            page_count INTEGER,
            content TEXT,
            tags TEXT DEFAULT '[]',
            version INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(relative_path)
        );
        """
    )
    await old_db.execute(
        "INSERT INTO workspace (id, name, description, user_id) VALUES (?, 'ws', '', ?)",
        (KB_ID, USER_ID),
    )
    await old_db.execute(
        "INSERT INTO documents (id, user_id, filename, title, path, relative_path, "
        "source_kind, file_type, status, content, tags, version, document_number) "
        "VALUES ('d1', ?, 'old.md', 'Old', '/wiki/', 'wiki/old.md', "
        "'wiki', 'md', 'ready', 'old body', '[]', 0, 1)",
        (USER_ID,),
    )
    await old_db.commit()
    await old_db.close()

    db = await create_pool(str(db_path))
    try:
        columns_cursor = await db.execute("PRAGMA table_info(documents)")
        columns = {row[1] for row in await columns_cursor.fetchall()}
        assert "knowledge_base_id" in columns
        assert "archived" in columns

        existing_cursor = await db.execute(
            "SELECT knowledge_base_id, archived FROM documents WHERE id = 'd1'"
        )
        assert await existing_cursor.fetchone() == (KB_ID, 0)

        repo = SQLiteDocumentRepository(db)
        existing = await repo.find_by_path(KB_ID, USER_ID, "old.md", "/wiki/")
        assert existing is not None
        assert existing["id"] == "d1"

        created = await repo.create_note(
            KB_ID, USER_ID, "new.md", "/wiki/inbox/", "New", "new body", ["email"]
        )
        assert created["knowledge_base_id"] == KB_ID
        assert created["archived"] == 0
    finally:
        await db.close()
