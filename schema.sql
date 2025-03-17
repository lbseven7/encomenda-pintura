-- Drop existing tables if they exist
drop table if exists public.bids;
drop table if exists public.auctions;
drop table if exists public.users;

-- Create users table
create table if not exists public.users (
  id uuid default gen_random_uuid() primary key,
  username text unique not null,
  password text not null,
  whatsapp text not null,
  created_at timestamptz default now()
);

-- Create auctions table
create table if not exists public.auctions (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  description text,
  image text,
  start_time timestamptz not null,
  end_time timestamptz not null,
  starting_bid decimal(10,2) not null,
  current_bid decimal(10,2) not null,
  is_featured boolean default false,
  artwork_dimensions text,
  artwork_technique text,
  artwork_year integer,
  artwork_status text default 'active',
  created_at timestamptz default now()
);

-- Create bids table
create table if not exists public.bids (
  id uuid default gen_random_uuid() primary key,
  auction_id uuid references public.auctions(id),
  user_id uuid references public.users(id),
  amount decimal(10,2) not null,
  bid_time timestamptz default now()
);