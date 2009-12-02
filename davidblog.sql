-- phpMyAdmin SQL Dump
-- version 3.2.3
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2009 年 12 月 02 日 12:59
-- 服务器版本: 5.0.84
-- PHP 版本: 5.2.11-pl1-gentoo

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `davidblog`
--

-- --------------------------------------------------------

--
-- 表的结构 `archives`
--

CREATE TABLE IF NOT EXISTS `archives` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `entryNum` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `archives`
--


-- --------------------------------------------------------

--
-- 表的结构 `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `slug` varchar(75) NOT NULL,
  `entryNum` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `categories`
--


-- --------------------------------------------------------

--
-- 表的结构 `comments`
--

CREATE TABLE IF NOT EXISTS `comments` (
  `id` int(11) NOT NULL auto_increment,
  `entryId` int(11) NOT NULL,
  `author` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `createdTime` datetime NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `entryId` (`entryId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `comments`
--


-- --------------------------------------------------------

--
-- 表的结构 `entries`
--

CREATE TABLE IF NOT EXISTS `entries` (
  `id` int(11) NOT NULL auto_increment,
  `title` varchar(255) NOT NULL,
  `content` longtext NOT NULL,
  `categoryId` int(11) NOT NULL,
  `createdTime` datetime NOT NULL,
  `modifiedTime` datetime NOT NULL,
  `viewNum` int(11) NOT NULL,
  `commentNum` int(11) NOT NULL,
  `slug` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `entries`
--


-- --------------------------------------------------------

--
-- 表的结构 `entry_tag`
--

CREATE TABLE IF NOT EXISTS `entry_tag` (
  `entryId` int(11) NOT NULL,
  `tagId` int(11) NOT NULL,
  KEY `entryId` (`entryId`,`tagId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `entry_tag`
--


-- --------------------------------------------------------

--
-- 表的结构 `links`
--

CREATE TABLE IF NOT EXISTS `links` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(70) NOT NULL,
  `url` varchar(255) NOT NULL,
  `createdTime` datetime NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `links`
--


-- --------------------------------------------------------

--
-- 表的结构 `tags`
--

CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `entryNum` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `tags`
--

