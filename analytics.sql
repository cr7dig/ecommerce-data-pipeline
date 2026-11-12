-- daily revenue and rolling 7-day average revenue
Select 
date(o.order_date) as order_day,
sum(oi.quantity * oi.item_price) as daily_revenue,
avg(sum(oi.quantity * oi.item_price)) OVER (order by date(o.order_date) rows between 6 preceding and current row) as rolling_7_day_avg_revenue
from orders o
join order_items oi on o.order_id = oi.order_id
group by date(o.order_date)
order by order_day desc;

-- top-selling products by category
with product_sales as(
Select 
p.category, p.product_name, sum(oi.quantity) as total_units_sold,
rank() over (partition by p.category order by sum(oi.quantity)desc) as rank_in_category
from products p
join order_items oi on p.product_id = oi.product_id
group by p.category, p.product_name)
select category, product_name, total_units_sold
from product_sales
where rank_in_category <=2;

-- high-value customer segmentation (customers with more orders and most spendings)
select u.user_id, u.name, count(distinct o.order_id) as total_orders, sum(oi.quantity * oi.item_price) as lifetime_spend
from users u 
join orders o on u.user_id = o.user_id 
join order_items oi on o.order_id = oi.order_id
group by u.user_id, u.name
HAVING COUNT(DISTINCT o.order_id) >= 3 AND SUM(oi.quantity * oi.item_price) > 200
ORDER BY lifetime_spend DESC;

-- top products bought per user
with u_p_ranking as (
select u.name as username, u.user_id,o.order_id, oi.order_item_id, p.product_name, sum(oi.quantity) as total_units_bought, rank()over(partition by u.user_id order by sum(oi.quantity) desc) as product_rank
from users u
join orders o on u.user_id = o.user_id
join order_items oi on o.order_id = oi.order_id
join products p on oi.product_id = p.product_id
group by u.user_id,u.name, o.order_id, oi.order_item_id, p.product_name
)
select username, order_id, product_name, total_units_bought, product_rank
from u_p_ranking
where product_rank <=3 
order by username, order_id,product_rank;