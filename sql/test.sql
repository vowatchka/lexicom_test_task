do
$$
declare
    rec record;
begin
    assert (select count(*) from full_names where status is null) = 0, 'в таблице full_names есть статусы null';

    for rec in (
        select
            s.name as short_name,
            s.status as original_status,
            f.name as full_name,
            f.status
        from full_names f
        join short_names s on s.name = split_part(f.name, '.', 1)
        order by s.name
    )
    loop
        assert rec.short_name = split_part(rec.full_name, '.', 1), 'названия не равны';
        assert rec.original_status = rec.status, 'статусы не равны';
    end loop;
end
$$;
