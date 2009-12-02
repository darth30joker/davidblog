-- phpMyAdmin SQL Dump
-- version 3.2.3
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2009 年 12 月 02 日 17:20
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
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- 转存表中的数据 `categories`
--

INSERT INTO `categories` (`id`, `name`, `slug`, `entryNum`) VALUES
(1, 'Python', 'python', 0),
(2, 'PHP', 'php', 0);

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
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- 转存表中的数据 `entries`
--

INSERT INTO `entries` (`id`, `title`, `content`, `categoryId`, `createdTime`, `modifiedTime`, `viewNum`, `commentNum`, `slug`) VALUES
(1, 'test entry', 'asdgsadgasdg', 1, '2009-12-02 13:31:27', '2009-12-02 13:31:32', 0, 0, 'test-entry'),
(2, 'second test entry', 'sdgasdgsadgsdgasdgas sdgasdg\r\nsdghasdhasdh\r\nsdhasdhsadh', 2, '2009-12-01 13:31:57', '2009-12-01 13:32:00', 0, 0, 'second-test-entry');

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

INSERT INTO `entry_tag` (`entryId`, `tagId`) VALUES
(1, 1),
(1, 2),
(2, 2);

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
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- 转存表中的数据 `links`
--

INSERT INTO `links` (`id`, `name`, `url`, `createdTime`) VALUES
(1, 'web.py官网', 'http://webpy.org/', '2009-12-02 16:26:36'),
(2, 'Python官网', 'http://python.org/', '2009-12-02 16:27:00');

-- --------------------------------------------------------

--
-- 表的结构 `tags`
--

CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `entryNum` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- 转存表中的数据 `tags`
--

INSERT INTO `tags` (`id`, `name`, `entryNum`) VALUES
(1, 'python', 1),
(2, 'test', 2);
