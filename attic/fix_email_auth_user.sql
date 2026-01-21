UPDATE auth_user
SET email=subquery.email
FROM (SELECT c.compet_email as email, u.id as user_id
      FROM auth_user as u, compet as c where u.id=c.user_id and u.email <> c.compet_email) AS subquery
WHERE auth_user.id=subquery.user_id;
