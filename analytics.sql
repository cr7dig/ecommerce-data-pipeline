Select 
date(o.order_date) as order_day,
sum(oi.quantity * oi.item_price) as daily_revenue,
avg(sum(oi.quantity * oi.item_price)) OVER (order by date(o.order_date) rows between 6 preceding and current row) as rolling_7_day_avg_revenue
from orders o
join order_items oi on o.order_id = oi.order_id
group by date(o.order_date)
order by order_day desc;

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